from __future__ import annotations

import json
from dataclasses import replace

import pytest

from tests.proof_fixtures import (
    BLOCK_HASH,
    CONTRACT,
    EVIDENCE_REF,
    TX_HASH,
    WRITER,
    evidence_proof,
)


def test_evidence_proof_to_dict_is_stable_json_compatible_and_canonical() -> None:
    proof = evidence_proof()

    first = proof.to_dict()
    second = proof.to_dict()

    assert first == second
    json.dumps(first)
    assert first["generated_at_utc"] == "2026-08-06T00:00:00Z"
    assert first["chain"]["contract_address"] == CONTRACT
    assert first["transaction"]["tx_hash"] == TX_HASH
    assert first["transaction"]["block_hash"] == BLOCK_HASH
    assert first["transaction"]["from"] == WRITER
    assert first["decoded_call"]["evidence_ref"] == EVIDENCE_REF
    assert first["transaction"]["effective_gas_price"] is None


def test_verified_proof_rejects_a_false_check() -> None:
    proof = evidence_proof()
    failed_checks = replace(proof.checks, receipt_successful=False)

    with pytest.raises(ValueError, match="every verification check"):
        replace(proof, checks=failed_checks)


def test_proof_rejects_naive_timestamp() -> None:
    proof = evidence_proof()

    with pytest.raises(ValueError, match="timezone-aware"):
        replace(proof, generated_at_utc=proof.generated_at_utc.replace(tzinfo=None)).to_dict()
