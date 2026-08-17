from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from hexbytes import HexBytes

from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import TransactionVerificationError
from blockchain_client.models import VerifiedAccess, VerifiedEvidence
from blockchain_client.proof_builder import TransactionProofBuilder
from tests.proof_fixtures import (
    CONTRACT,
    EVIDENCE_HASH,
    EVIDENCE_REF,
    TX_HASH,
    UPLOADER_REF,
    WRITER,
)

OFFICER_REF = "0x" + "55" * 32
SESSION_REF = "0x" + "66" * 32


class FakeVerifier:
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    def verify_evidence_transaction(self, tx_hash: str) -> VerifiedEvidence:
        self.calls.append("verify-evidence")
        if self.fail:
            raise TransactionVerificationError("verification failed")
        return VerifiedEvidence(
            EVIDENCE_REF,
            EVIDENCE_HASH,
            UPLOADER_REF,
            TX_HASH,
            100,
            datetime(2026, 8, 6, tzinfo=UTC),
            WRITER,
            2,
            "verified",
        )

    def verify_access_transaction(self, tx_hash: str) -> VerifiedAccess:
        self.calls.append("verify-access")
        if self.fail:
            raise TransactionVerificationError("verification failed")
        return VerifiedAccess(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            TX_HASH,
            100,
            datetime(2026, 8, 6, tzinfo=UTC),
            WRITER,
            2,
            "verified",
        )


def make_client(operation: str) -> Any:
    function_name = "recordEvidence" if operation == "evidence" else "recordAccess"
    params = {"evidenceRef": HexBytes(EVIDENCE_REF)}
    if operation == "evidence":
        params["evidenceHash"] = HexBytes(EVIDENCE_HASH)
        params["uploaderRef"] = HexBytes(UPLOADER_REF)
    else:
        params["officerRef"] = HexBytes(OFFICER_REF)
        params["accessSessionRef"] = HexBytes(SESSION_REF)
    tx = {"from": WRITER, "to": CONTRACT, "input": "0x1234"}
    receipt = {
        "status": 1,
        "blockNumber": 100,
        "transactionHash": HexBytes(TX_HASH),
        "gasUsed": 75000,
        "effectiveGasPrice": 7,
    }
    block = {
        "hash": HexBytes("0x" + "cd" * 32),
        "timestamp": int(datetime(2026, 8, 6, tzinfo=UTC).timestamp()),
    }
    eth = SimpleNamespace(
        get_transaction=lambda tx_hash: tx,
        get_transaction_receipt=lambda tx_hash: receipt,
        get_block=lambda number: block,
    )
    return SimpleNamespace(
        settings=BlockchainClientSettings(
            provider_uri="http://127.0.0.1:8545",
            chain_id=20260720,
            contract_address=CONTRACT,
            artifact_path=Path("tests/fixtures/EvidenceRegistry.json"),
        ),
        web3=SimpleNamespace(eth=eth),
        contract=SimpleNamespace(
            address=CONTRACT,
            decode_function_input=lambda value: (SimpleNamespace(fn_name=function_name), params),
        ),
    )


def test_build_evidence_proof_collects_metadata_after_verification() -> None:
    verifier = FakeVerifier()
    proof = TransactionProofBuilder(make_client("evidence"), verifier).build_evidence_proof(TX_HASH)

    assert verifier.calls == ["verify-evidence"]
    assert proof.function_name == "recordEvidence"
    assert proof.evidence_ref == EVIDENCE_REF
    assert proof.evidence_hash == EVIDENCE_HASH
    assert proof.uploader_ref == UPLOADER_REF
    assert proof.transaction.gas_used == 75000
    assert proof.transaction.effective_gas_price == 7
    assert proof.checks.all_passed()


def test_build_access_proof_collects_verified_references() -> None:
    verifier = FakeVerifier()
    proof = TransactionProofBuilder(make_client("access"), verifier).build_access_proof(TX_HASH)

    assert verifier.calls == ["verify-access"]
    assert proof.function_name == "recordAccess"
    assert proof.officer_ref == OFFICER_REF
    assert proof.access_session_ref == SESSION_REF


def test_builder_propagates_verifier_failure_before_loading_metadata() -> None:
    verifier = FakeVerifier(fail=True)
    client = make_client("evidence")
    client.web3.eth.get_transaction = lambda tx_hash: pytest.fail("metadata loaded too early")

    with pytest.raises(TransactionVerificationError, match="verification failed"):
        TransactionProofBuilder(client, verifier).build_evidence_proof(TX_HASH)

    assert verifier.calls == ["verify-evidence"]
