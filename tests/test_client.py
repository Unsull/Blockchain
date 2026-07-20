from pathlib import Path
from types import MethodType, SimpleNamespace

from eth_account import Account
from hexbytes import HexBytes

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

    assert client.signer.address == Account.from_key(private_key).address


def test_get_evidence_validates_connection_before_query() -> None:
    calls: list[str] = []
    client = object.__new__(BlockchainClient)

    def validate_connection(self: BlockchainClient) -> None:
        calls.append("validated")

    class EvidenceCall:
        def call(self) -> tuple[HexBytes, int, str, bool]:
            calls.append("queried")
            return (
                HexBytes("0x" + "aa" * 32),
                1,
                "0x0000000000000000000000000000000000000001",
                True,
            )

    client.validate_connection = MethodType(validate_connection, client)
    client.contract = SimpleNamespace(
        functions=SimpleNamespace(getEvidence=lambda evidence: EvidenceCall())
    )

    result = client.get_evidence("0x" + "11" * 32)

    assert calls == ["validated", "queried"]
    assert result["static_hash"] == "0x" + "aa" * 32


def test_health_check_reports_disconnected_provider() -> None:
    client = object.__new__(BlockchainClient)
    client.web3 = SimpleNamespace(is_connected=lambda: False)
    client.contract = SimpleNamespace(address="0x0000000000000000000000000000000000000001")

    health = client.health_check()

    assert health.connected is False
    assert health.chain_id is None
    assert health.contract_deployed is False
