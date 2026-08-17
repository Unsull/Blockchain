from __future__ import annotations

from hashlib import sha256
from uuid import UUID

import pytest

from blockchain_client import (
    derive_access_session_ref,
    derive_actor_ref,
    derive_evidence_ref,
)
from blockchain_client.exceptions import ReferenceValidationError
from blockchain_client.references import normalize_bytes32

UUID_VALUE = UUID("12345678-1234-5678-9abc-def012345678")
OTHER_UUID = UUID("87654321-4321-6789-abcd-ef0123456789")


def test_evidence_ref_accepts_uuid_object() -> None:
    result = derive_evidence_ref(UUID_VALUE)
    assert result == normalize_bytes32(result)


def test_evidence_ref_accepts_uuid_string() -> None:
    assert derive_evidence_ref(str(UUID_VALUE)) == derive_evidence_ref(UUID_VALUE)


def test_evidence_ref_is_deterministic() -> None:
    assert derive_evidence_ref(UUID_VALUE) == derive_evidence_ref(UUID_VALUE)


def test_evidence_ref_matches_watermark_formula() -> None:
    expected = "0x" + sha256(str(UUID_VALUE).encode("utf-8")).hexdigest()
    assert derive_evidence_ref(UUID_VALUE) == expected


def test_canonical_uuid_representations_match() -> None:
    uppercase = str(UUID_VALUE).upper()
    compact = UUID_VALUE.hex
    assert derive_evidence_ref(uppercase) == derive_evidence_ref(compact)


@pytest.mark.parametrize("value", ["not-a-uuid", "", "1234"])
def test_invalid_uuid_is_rejected(value: str) -> None:
    with pytest.raises(ReferenceValidationError, match="valid UUID"):
        derive_evidence_ref(value)


def test_actor_ref_is_deterministic_and_uses_expected_formula() -> None:
    expected = "0x" + sha256(b"DEVA:USER:v1:" + UUID_VALUE.bytes).hexdigest()
    assert derive_actor_ref(UUID_VALUE) == expected
    assert derive_actor_ref(UUID_VALUE) == derive_actor_ref(str(UUID_VALUE))


def test_access_session_ref_is_deterministic_and_uses_expected_formula() -> None:
    expected = "0x" + sha256(b"DEVA:ACCESS:v1:" + UUID_VALUE.bytes).hexdigest()
    assert derive_access_session_ref(UUID_VALUE) == expected
    assert derive_access_session_ref(UUID_VALUE) == derive_access_session_ref(str(UUID_VALUE))


@pytest.mark.parametrize(
    "derive",
    [derive_evidence_ref, derive_actor_ref, derive_access_session_ref],
)
def test_different_uuids_produce_different_references(derive: object) -> None:
    assert callable(derive)
    assert derive(UUID_VALUE) != derive(OTHER_UUID)


def test_domain_separation_distinguishes_actor_and_access_session() -> None:
    assert derive_actor_ref(UUID_VALUE) != derive_access_session_ref(UUID_VALUE)


def test_all_outputs_are_valid_bytes32() -> None:
    outputs = (
        derive_evidence_ref(UUID_VALUE),
        derive_actor_ref(UUID_VALUE),
        derive_access_session_ref(UUID_VALUE),
    )
    assert all(normalize_bytes32(value) == value for value in outputs)
