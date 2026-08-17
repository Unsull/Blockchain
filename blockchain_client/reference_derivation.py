"""Canonical opaque bytes32 derivation from application UUID identifiers."""

from hashlib import sha256
from uuid import UUID

from blockchain_client.exceptions import ReferenceValidationError
from blockchain_client.references import normalize_bytes32

UUIDInput = UUID | str


def derive_evidence_ref(evidence_id: UUIDInput) -> str:
    """Derive the Watermark-compatible evidence reference."""

    value = _parse_uuid(evidence_id, "evidence_id")
    # Blockchain integration:
    # evidenceRef intentionally matches the existing Static Watermark
    # SHA-256(evidence_id) representation.
    digest = sha256(str(value).encode("utf-8")).hexdigest()
    return normalize_bytes32(f"0x{digest}", "evidence_ref")


def derive_actor_ref(user_id: UUIDInput) -> str:
    """Derive the shared uploaderRef and officerRef representation."""

    value = _parse_uuid(user_id, "user_id")
    # Blockchain integration:
    # Domain separation prevents user and access UUIDs from producing the same
    # on-chain reference even if their underlying UUID values are identical.
    digest = sha256(b"DEVA:USER:v1:" + value.bytes).hexdigest()
    return normalize_bytes32(f"0x{digest}", "actor_ref")


def derive_access_session_ref(access_log_id: UUIDInput) -> str:
    """Derive the domain-separated accessSessionRef representation."""

    value = _parse_uuid(access_log_id, "access_log_id")
    digest = sha256(b"DEVA:ACCESS:v1:" + value.bytes).hexdigest()
    return normalize_bytes32(f"0x{digest}", "access_session_ref")


def _parse_uuid(value: UUIDInput, field_name: str) -> UUID:
    if isinstance(value, UUID):
        return value
    if not isinstance(value, str):
        raise ReferenceValidationError(f"{field_name} must be a UUID or UUID string")
    try:
        return UUID(value)
    except (AttributeError, ValueError) as exc:
        raise ReferenceValidationError(f"{field_name} must be a valid UUID") from exc
