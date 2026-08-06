"""Python client for the EvidenceRegistry blockchain module."""

from blockchain_client.client import BlockchainClient
from blockchain_client.config import BlockchainClientSettings
from blockchain_client.models import (
    BlockchainHealth,
    TransactionResult,
    VerifiedAccess,
    VerifiedEvidence,
)
from blockchain_client.proof_builder import TransactionProofBuilder
from blockchain_client.proof_models import AccessTransactionProof, EvidenceTransactionProof
from blockchain_client.signer import LocalPrivateKeySigner, TransactionSigner

__all__ = [
    "BlockchainClient",
    "BlockchainClientSettings",
    "BlockchainHealth",
    "AccessTransactionProof",
    "EvidenceTransactionProof",
    "LocalPrivateKeySigner",
    "TransactionResult",
    "TransactionProofBuilder",
    "TransactionSigner",
    "VerifiedAccess",
    "VerifiedEvidence",
]
