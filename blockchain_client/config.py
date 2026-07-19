"""Configuration for the blockchain client."""

from dataclasses import dataclass
from pathlib import Path

from eth_utils import is_address

from blockchain_client.exceptions import ConfigurationError


@dataclass(frozen=True)
class BlockchainClientSettings:
    """Validated settings required to connect and sign transactions."""

    provider_uri: str
    chain_id: int
    contract_address: str
    signer_private_key: str
    artifact_path: Path
    request_timeout_seconds: int = 30
    confirmation_blocks: int = 0

    def validate(self) -> None:
        if not self.provider_uri:
            raise ConfigurationError("provider_uri is required")
        if self.chain_id <= 0:
            raise ConfigurationError("chain_id must be positive")
        if not is_address(self.contract_address):
            raise ConfigurationError("contract_address must be a valid EVM address")
        if not self.signer_private_key:
            raise ConfigurationError("signer_private_key is required")
        if not self.artifact_path.exists():
            raise ConfigurationError(f"artifact_path does not exist: {self.artifact_path}")
        if self.request_timeout_seconds <= 0:
            raise ConfigurationError("request_timeout_seconds must be positive")
        if self.confirmation_blocks < 0:
            raise ConfigurationError("confirmation_blocks cannot be negative")
