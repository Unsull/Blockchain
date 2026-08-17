"""Serializable proof models for verified EvidenceRegistry transactions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Literal

from web3 import Web3

from blockchain_client.references import bytes32_to_hex, normalize_tx_hash

SCHEMA_VERSION = "1.0"


def _canonical_address(value: str, field_name: str) -> str:
    if not Web3.is_address(value):
        raise ValueError(f"{field_name} must be a valid EVM address")
    return value.lower()


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class VerificationChecks:
    transaction_found: bool
    receipt_successful: bool
    contract_target_matches: bool
    function_matches: bool
    input_event_matches: bool
    event_receipt_matches: bool
    writer_sender_matches: bool
    event_state_matches: bool
    confirmations_sufficient: bool

    def all_passed(self) -> bool:
        return all(self.to_dict().values())

    def to_dict(self) -> dict[str, bool]:
        return {
            "transaction_found": self.transaction_found,
            "receipt_successful": self.receipt_successful,
            "contract_target_matches": self.contract_target_matches,
            "function_matches": self.function_matches,
            "input_event_matches": self.input_event_matches,
            "event_receipt_matches": self.event_receipt_matches,
            "writer_sender_matches": self.writer_sender_matches,
            "event_state_matches": self.event_state_matches,
            "confirmations_sufficient": self.confirmations_sufficient,
        }


@dataclass(frozen=True)
class TransactionMetadata:
    tx_hash: str
    sender: str
    target: str
    receipt_status: int
    block_number: int
    block_hash: str
    block_timestamp_utc: datetime
    gas_used: int
    effective_gas_price: int | None
    confirmations: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "tx_hash", normalize_tx_hash(self.tx_hash))
        object.__setattr__(self, "sender", _canonical_address(self.sender, "sender"))
        object.__setattr__(self, "target", _canonical_address(self.target, "target"))
        object.__setattr__(self, "block_hash", normalize_tx_hash(self.block_hash))
        if self.receipt_status not in (0, 1):
            raise ValueError("receipt_status must be 0 or 1")
        if min(self.block_number, self.gas_used, self.confirmations) < 0:
            raise ValueError("transaction numeric fields cannot be negative")

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "from": self.sender,
            "to": self.target,
            "receipt_status": self.receipt_status,
            "block_number": self.block_number,
            "block_hash": self.block_hash,
            "block_timestamp_utc": _utc_iso(self.block_timestamp_utc),
            "gas_used": self.gas_used,
            "effective_gas_price": self.effective_gas_price,
            "confirmations": self.confirmations,
        }


@dataclass(frozen=True)
class ChainMetadata:
    chain_id: int
    contract_address: str

    def __post_init__(self) -> None:
        if self.chain_id <= 0:
            raise ValueError("chain_id must be positive")
        object.__setattr__(
            self,
            "contract_address",
            _canonical_address(self.contract_address, "contract_address"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"chain_id": self.chain_id, "contract_address": self.contract_address}


@dataclass(frozen=True)
class EvidenceTransactionProof:
    schema_version: str
    generated_at_utc: datetime
    operation: Literal["recordEvidence"]
    verification_status: Literal["verified"]
    chain: ChainMetadata
    transaction: TransactionMetadata
    function_name: str
    evidence_ref: str
    evidence_hash: str
    uploader_ref: str
    writer_address: str
    checks: VerificationChecks

    def __post_init__(self) -> None:
        _validate_common(self.schema_version, self.operation, self.verification_status, self.checks)
        if self.function_name != "recordEvidence":
            raise ValueError("evidence proof function must be recordEvidence")
        object.__setattr__(self, "evidence_ref", bytes32_to_hex(self.evidence_ref))
        object.__setattr__(self, "evidence_hash", bytes32_to_hex(self.evidence_hash))
        object.__setattr__(self, "uploader_ref", bytes32_to_hex(self.uploader_ref))
        object.__setattr__(
            self, "writer_address", _canonical_address(self.writer_address, "writer_address")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at_utc": _utc_iso(self.generated_at_utc),
            "operation": self.operation,
            "verification_status": self.verification_status,
            "chain": self.chain.to_dict(),
            "transaction": self.transaction.to_dict(),
            "decoded_call": {
                "function_name": self.function_name,
                "evidence_ref": self.evidence_ref,
                "evidence_hash": self.evidence_hash,
                "uploader_ref": self.uploader_ref,
            },
            "writer_address": self.writer_address,
            "checks": self.checks.to_dict(),
        }


@dataclass(frozen=True)
class AccessTransactionProof:
    schema_version: str
    generated_at_utc: datetime
    operation: Literal["recordAccess"]
    verification_status: Literal["verified"]
    chain: ChainMetadata
    transaction: TransactionMetadata
    function_name: str
    evidence_ref: str
    officer_ref: str
    access_session_ref: str
    writer_address: str
    checks: VerificationChecks

    def __post_init__(self) -> None:
        _validate_common(self.schema_version, self.operation, self.verification_status, self.checks)
        if self.function_name != "recordAccess":
            raise ValueError("access proof function must be recordAccess")
        object.__setattr__(self, "evidence_ref", bytes32_to_hex(self.evidence_ref))
        object.__setattr__(self, "officer_ref", bytes32_to_hex(self.officer_ref))
        object.__setattr__(self, "access_session_ref", bytes32_to_hex(self.access_session_ref))
        object.__setattr__(
            self, "writer_address", _canonical_address(self.writer_address, "writer_address")
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "generated_at_utc": _utc_iso(self.generated_at_utc),
            "operation": self.operation,
            "verification_status": self.verification_status,
            "chain": self.chain.to_dict(),
            "transaction": self.transaction.to_dict(),
            "decoded_call": {
                "function_name": self.function_name,
                "evidence_ref": self.evidence_ref,
                "officer_ref": self.officer_ref,
                "access_session_ref": self.access_session_ref,
            },
            "writer_address": self.writer_address,
            "checks": self.checks.to_dict(),
        }


TransactionProof = EvidenceTransactionProof | AccessTransactionProof


def _validate_common(
    schema_version: str,
    operation: str,
    verification_status: str,
    checks: VerificationChecks,
) -> None:
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if operation not in {"recordEvidence", "recordAccess"}:
        raise ValueError("unsupported proof operation")
    if verification_status != "verified" or not checks.all_passed():
        raise ValueError("verified proofs require every verification check to pass")
