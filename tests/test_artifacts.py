from pathlib import Path

import pytest

from blockchain_client.artifacts import load_contract_abi
from blockchain_client.exceptions import ConfigurationError


def test_load_contract_abi(tmp_path: Path) -> None:
    artifact = tmp_path / "EvidenceRegistry.json"
    artifact.write_text('{"abi": [{"type": "function"}]}', encoding="utf-8")
    assert load_contract_abi(artifact) == [{"type": "function"}]


def test_load_contract_abi_rejects_missing_abi(tmp_path: Path) -> None:
    artifact = tmp_path / "EvidenceRegistry.json"
    artifact.write_text("{}", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_contract_abi(artifact)
