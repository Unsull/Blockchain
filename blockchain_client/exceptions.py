"""Typed exceptions raised by the blockchain client."""


class BlockchainClientError(Exception):
    """Base exception for blockchain client failures."""


class ConfigurationError(BlockchainClientError):
    """Raised when client settings are invalid."""


class ReferenceValidationError(BlockchainClientError):
    """Raised when an opaque reference is not a non-zero bytes32 value."""


class ContractConnectionError(BlockchainClientError):
    """Raised when provider, chain, or deployed contract validation fails."""


class TransactionSubmissionError(BlockchainClientError):
    """Raised when transaction construction, signing, or submission fails."""


class TransactionVerificationError(BlockchainClientError):
    """Raised when a transaction cannot be verified against contract state/events."""
