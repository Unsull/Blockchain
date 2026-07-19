"""Typed result models returned by the blockchain client."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TransactionResult:
    """Validated transaction submission result."""

    tx_hash: str
    block_number: int
    block_timestamp: datetime
    contract_address: str
    chain_id: int
    confirmations: int
    event: dict


@dataclass(frozen=True)
class VerifiedEvidence:
    """Verified recordEvidence transaction details."""

    evidence_ref: str
    static_hash: str
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
