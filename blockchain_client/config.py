"""Configuration for the blockchain client."""

from dataclasses import dataclass
from pathlib import Path

from web3 import Web3

from blockchain_client.exceptions import ConfigurationError


@dataclass(frozen=True)
class BlockchainClientSettings:
    """Validated settings required to connect and sign transactions."""

    provider_uri: str
    chain_id: int
    contract_address: str
    artifact_path: Path
    request_timeout_seconds: int = 30
    confirmation_blocks: int = 0
    confirmation_poll_interval_seconds: float = 1.0
    confirmation_timeout_seconds: int = 120
    gas_estimate_multiplier: float = 1.2
    max_fee_per_gas: int | None = None
    max_priority_fee_per_gas: int | None = None
    legacy_gas_price: int | None = None
    signer_private_key: str | None = None

    def validate(self) -> None:
        if not self.provider_uri:
            raise ConfigurationError("provider_uri is required")
        if self.chain_id <= 0:
            raise ConfigurationError("chain_id must be positive")
        if not Web3.is_address(self.contract_address):
            raise ConfigurationError("contract_address must be a valid EVM address")
        if int(self.contract_address, 16) == 0:
            raise ConfigurationError("contract_address cannot be the zero address")
        if not self.artifact_path.exists():
            raise ConfigurationError(f"artifact_path does not exist: {self.artifact_path}")
        if self.request_timeout_seconds <= 0:
            raise ConfigurationError("request_timeout_seconds must be positive")
        if self.confirmation_blocks < 0:
            raise ConfigurationError("confirmation_blocks cannot be negative")
        if self.confirmation_poll_interval_seconds <= 0:
            raise ConfigurationError("confirmation_poll_interval_seconds must be positive")
        if self.confirmation_timeout_seconds <= 0:
            raise ConfigurationError("confirmation_timeout_seconds must be positive")
        if self.gas_estimate_multiplier < 1:
            raise ConfigurationError("gas_estimate_multiplier must be >= 1")
        fee_values = [
            self.max_fee_per_gas,
            self.max_priority_fee_per_gas,
            self.legacy_gas_price,
        ]
        if any(value is not None and value < 0 for value in fee_values):
            raise ConfigurationError("fee values cannot be negative")
        if self.signer_private_key is not None and not self.signer_private_key.strip():
            raise ConfigurationError("signer_private_key cannot be empty when provided")
        has_eip1559 = self.max_fee_per_gas is not None or self.max_priority_fee_per_gas is not None
        if has_eip1559 and self.legacy_gas_price is not None:
            raise ConfigurationError("legacy_gas_price cannot be combined with EIP-1559 fees")
