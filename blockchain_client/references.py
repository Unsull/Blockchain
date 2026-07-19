"""Opaque bytes32 reference validation helpers."""

from blockchain_client.exceptions import ReferenceValidationError

ZERO_BYTES32 = "0x" + "0" * 64


def normalize_bytes32(value: str, field_name: str = "reference") -> str:
    """Normalize and validate a hex bytes32 string."""

    candidate = value.strip()
    if not candidate.startswith("0x"):
        candidate = f"0x{candidate}"
    if len(candidate) != 66:
        raise ReferenceValidationError(f"{field_name} must be 32 bytes")
    try:
        int(candidate[2:], 16)
    except ValueError as exc:
        raise ReferenceValidationError(f"{field_name} must be hex encoded") from exc
    if candidate.lower() == ZERO_BYTES32:
        raise ReferenceValidationError(f"{field_name} cannot be zero bytes32")
    return candidate.lower()


def normalize_tx_hash(value: str) -> str:
    """Normalize and validate a transaction hash."""

    candidate = value.strip()
    if not candidate.startswith("0x"):
        candidate = f"0x{candidate}"
    if len(candidate) != 66:
        raise ReferenceValidationError("tx_hash must be 32 bytes")
    try:
        int(candidate[2:], 16)
    except ValueError as exc:
        raise ReferenceValidationError("tx_hash must be hex encoded") from exc
    return candidate.lower()
