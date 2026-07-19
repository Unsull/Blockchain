import pytest

from blockchain_client.exceptions import ReferenceValidationError
from blockchain_client.references import normalize_bytes32, normalize_tx_hash


def test_normalize_bytes32_adds_prefix() -> None:
    value = "1" * 64
    assert normalize_bytes32(value) == "0x" + value


@pytest.mark.parametrize("value", ["0x1234", "0x" + "0" * 64, "0x" + "z" * 64])
def test_normalize_bytes32_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ReferenceValidationError):
        normalize_bytes32(value)


def test_normalize_tx_hash_accepts_zero_hash_for_lookup() -> None:
    assert normalize_tx_hash("0" * 64) == "0x" + "0" * 64
