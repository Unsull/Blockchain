"""Typed result models returned by the blockchain client."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class TransactionResult:
    """Validated transaction submission result."""

    tx_hash: str
    block_number: int
    block_timestamp: datetime
    contract_address: str
    chain_id: int
    confirmations: int
    event: dict[str, Any]


@dataclass(frozen=True)
class BlockchainHealth:
    """Connection and deployment health details."""

    connected: bool
    chain_id: int | None
    latest_block: int | None
    contract_address: str
    contract_deployed: bool


@dataclass(frozen=True)
class EvidenceRecordedEvent:
    """Canonical EvidenceRecorded custody event."""

    evidence_ref: str
    evidence_hash: str
    uploader_ref: str
    recorded_at: int
    writer: str
    tx_hash: str
    block_number: int
    transaction_index: int
    log_index: int


@dataclass(frozen=True)
class EvidenceAccessEvent:
    """Canonical EvidenceAccessRecorded custody event."""

    evidence_ref: str
    officer_ref: str
    access_session_ref: str
    recorded_at: int
    writer: str
    tx_hash: str
    block_number: int
    transaction_index: int
    log_index: int


@dataclass(frozen=True)
class VerifiedEvidence:
    """Verified recordEvidence transaction details."""

    evidence_ref: str
    evidence_hash: str
    uploader_ref: str
    tx_hash: str
    block_number: int
    block_timestamp: datetime
    writer: str
    confirmations: int
    status: str


@dataclass(frozen=True)
class VerifiedAccess:
    """Verified recordAccess transaction details."""

    evidence_ref: str
    officer_ref: str
    access_session_ref: str
    tx_hash: str
    block_number: int
    block_timestamp: datetime
    writer: str
    confirmations: int
    status: str
