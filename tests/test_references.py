import pytest
from hexbytes import HexBytes

from blockchain_client.exceptions import ReferenceValidationError
from blockchain_client.references import bytes32_to_hex, normalize_bytes32, normalize_tx_hash


def test_normalize_bytes32_adds_prefix() -> None:
    value = "1" * 64
    assert normalize_bytes32(value) == "0x" + value


@pytest.mark.parametrize("value", ["0x1234", "0x" + "0" * 64, "0x" + "z" * 64])
def test_normalize_bytes32_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ReferenceValidationError):
        normalize_bytes32(value)


def test_normalize_tx_hash_accepts_zero_hash_for_lookup() -> None:
    assert normalize_tx_hash("0" * 64) == "0x" + "0" * 64


@pytest.mark.parametrize(
    "value",
    [
        "A" * 64,
        bytes.fromhex("AA" * 32),
        HexBytes("0x" + "AA" * 32),
    ],
)
def test_bytes32_to_hex_returns_canonical_lowercase(value: bytes | HexBytes | str) -> None:
    assert bytes32_to_hex(value) == "0x" + "aa" * 32


@pytest.mark.parametrize("value", ["0x1234", b"\x01", "0x" + "z" * 64])
def test_bytes32_to_hex_rejects_invalid_values(value: bytes | str) -> None:
    with pytest.raises(ReferenceValidationError):
        bytes32_to_hex(value)
