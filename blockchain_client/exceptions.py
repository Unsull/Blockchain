"""Typed exceptions raised by the blockchain client."""


class BlockchainClientError(Exception):
    """Base exception for blockchain client failures."""


class ConfigurationError(BlockchainClientError):
    """Raised when client settings are invalid."""


class ReferenceValidationError(BlockchainClientError):
    """Raised when an opaque reference is not a non-zero bytes32 value."""


class ContractConnectionError(BlockchainClientError):
    """Raised when provider, chain, or deployed contract validation fails."""


class ChainIdMismatchError(ContractConnectionError):
    """Raised when the connected chain ID does not match settings."""


class ContractNotDeployedError(ContractConnectionError):
    """Raised when no bytecode exists at the configured contract address."""


class TransactionBuildError(BlockchainClientError):
    """Raised when a transaction cannot be built."""


class TransactionSigningError(BlockchainClientError):
    """Raised when the signer cannot sign a transaction."""


class TransactionSubmissionError(BlockchainClientError):
    """Raised when transaction submission fails."""


class TransactionTimeoutError(TransactionSubmissionError):
    """Raised while waiting for a transaction receipt times out."""


class TransactionRevertedError(TransactionSubmissionError):
    """Raised when a transaction receipt has status 0."""


class TransactionConfirmationTimeoutError(TransactionSubmissionError):
    """Raised when required confirmation blocks are not reached in time."""


class EventDecodeError(TransactionSubmissionError):
    """Raised when expected events cannot be decoded from a receipt."""


class EventValidationError(TransactionSubmissionError):
    """Raised when decoded event data does not match transaction inputs."""


class NonceError(TransactionSubmissionError):
    """Raised for nonce allocation or nonce conflict failures."""


class TransactionVerificationError(BlockchainClientError):
    """Raised when a transaction cannot be verified against contract state/events."""
