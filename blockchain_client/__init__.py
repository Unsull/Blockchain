"""Python client for the EvidenceRegistry blockchain module."""

from blockchain_client.client import BlockchainClient
from blockchain_client.config import BlockchainClientSettings
from blockchain_client.models import (
    BlockchainHealth,
    EvidenceAccessEvent,
    EvidenceRecordedEvent,
    TransactionResult,
    VerifiedAccess,
    VerifiedEvidence,
)
from blockchain_client.proof_builder import TransactionProofBuilder
from blockchain_client.proof_models import AccessTransactionProof, EvidenceTransactionProof
from blockchain_client.reference_derivation import (
    derive_access_session_ref,
    derive_actor_ref,
    derive_evidence_ref,
)
from blockchain_client.signer import LocalPrivateKeySigner, TransactionSigner

__all__ = [
    "BlockchainClient",
    "BlockchainClientSettings",
    "BlockchainHealth",
    "EvidenceAccessEvent",
    "EvidenceRecordedEvent",
    "AccessTransactionProof",
    "EvidenceTransactionProof",
    "derive_access_session_ref",
    "derive_actor_ref",
    "derive_evidence_ref",
    "LocalPrivateKeySigner",
    "TransactionResult",
    "TransactionProofBuilder",
    "TransactionSigner",
    "VerifiedAccess",
    "VerifiedEvidence",
]
