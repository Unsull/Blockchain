from pathlib import Path

import pytest

from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import ConfigurationError


def valid_settings(tmp_path: Path) -> BlockchainClientSettings:
    artifact = tmp_path / "artifact.json"
    artifact.write_text('{"abi": []}', encoding="utf-8")
    return BlockchainClientSettings(
        provider_uri="http://127.0.0.1:8545",
        chain_id=31337,
        contract_address="0x0000000000000000000000000000000000000001",
        signer_private_key="0x" + "1" * 64,
        artifact_path=artifact,
    )


def test_valid_settings_pass(tmp_path: Path) -> None:
    valid_settings(tmp_path).validate()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_uri", ""),
        ("chain_id", 0),
        ("contract_address", "not-an-address"),
        ("signer_private_key", ""),
    ],
)
def test_invalid_settings_fail(tmp_path: Path, field: str, value: object) -> None:
    settings = valid_settings(tmp_path)
    data = settings.__dict__ | {field: value}
    with pytest.raises(ConfigurationError):
        BlockchainClientSettings(**data).validate()


def test_missing_artifact_path_fails(tmp_path: Path) -> None:
    settings = valid_settings(tmp_path)
    data = settings.__dict__ | {"artifact_path": tmp_path / "missing.json"}
    with pytest.raises(ConfigurationError):
        BlockchainClientSettings(**data).validate()
