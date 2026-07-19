from pathlib import Path

from eth_account import Account

from blockchain_client import BlockchainClient, BlockchainClientSettings


def test_client_derives_signer_address() -> None:
    private_key = "0x" + "1" * 64
    settings = BlockchainClientSettings(
        provider_uri="http://127.0.0.1:8545",
        chain_id=31337,
        contract_address="0x0000000000000000000000000000000000000001",
        signer_private_key=private_key,
        artifact_path=Path("tests/fixtures/EvidenceRegistry.json"),
    )

    client = BlockchainClient(settings)

    assert client.account.address == Account.from_key(private_key).address
