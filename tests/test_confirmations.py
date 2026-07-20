from pathlib import Path
from types import SimpleNamespace

import pytest

from blockchain_client.client import BlockchainClient
from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import TransactionConfirmationTimeoutError


def make_client_like(current_block: int, confirmations: int) -> BlockchainClient:
    client = object.__new__(BlockchainClient)
    client.settings = BlockchainClientSettings(
        provider_uri="http://127.0.0.1:8545",
        chain_id=31337,
        contract_address="0x0000000000000000000000000000000000000001",
        artifact_path=Path("tests/fixtures/EvidenceRegistry.json"),
        confirmation_blocks=confirmations,
        confirmation_poll_interval_seconds=0.001,
        confirmation_timeout_seconds=1,
    )
    client.web3 = SimpleNamespace(eth=SimpleNamespace(block_number=current_block))
    return client


def test_wait_for_confirmations_returns_immediately_when_zero_required() -> None:
    client = make_client_like(current_block=12, confirmations=0)

    assert client._wait_for_confirmations(10) == 2


def test_wait_for_confirmations_returns_when_target_reached() -> None:
    client = make_client_like(current_block=15, confirmations=5)

    assert client._wait_for_confirmations(10) == 5


def test_wait_for_confirmations_times_out() -> None:
    client = make_client_like(current_block=11, confirmations=5)
    client.settings = BlockchainClientSettings(
        provider_uri=client.settings.provider_uri,
        chain_id=client.settings.chain_id,
        contract_address=client.settings.contract_address,
        artifact_path=client.settings.artifact_path,
        confirmation_blocks=5,
        confirmation_poll_interval_seconds=0.001,
        confirmation_timeout_seconds=1,
    )

    with pytest.raises(TransactionConfirmationTimeoutError):
        client._wait_for_confirmations(10)
