from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from hexbytes import HexBytes
from web3.exceptions import TransactionNotFound

from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import TransactionVerificationError
from blockchain_client.transaction_verifier import TransactionVerifier

TX_HASH = "0x" + "ab" * 32
OTHER_TX_HASH = HexBytes("0x" + "bc" * 32)
CONTRACT = "0x" + "44" * 20
OTHER_CONTRACT = "0x" + "45" * 20
WRITER = "0x" + "33" * 20
OTHER_WRITER = "0x" + "34" * 20
EVIDENCE_REF = "0x" + "11" * 32
STATIC_HASH = "0x" + "22" * 32
OFFICER_REF = "0x" + "55" * 32
SESSION_REF = "0x" + "66" * 32


class EventFactory:
    def __init__(self, events: list[dict[str, Any]]) -> None:
        self.events = events

    def __call__(self) -> EventFactory:
        return self

    def process_receipt(self, receipt: dict[str, Any]) -> list[dict[str, Any]]:
        return self.events


def make_context(operation: str = "evidence") -> tuple[TransactionVerifier, dict[str, Any]]:
    tx = {"to": CONTRACT, "from": WRITER, "input": "0x1234"}
    receipt = {
        "status": 1,
        "blockNumber": 10,
        "transactionHash": HexBytes(TX_HASH),
    }
    if operation == "evidence":
        function_name = "recordEvidence"
        params = {"evidenceRef": HexBytes(EVIDENCE_REF), "staticHash": HexBytes(STATIC_HASH)}
        args = {
            "evidenceRef": HexBytes(EVIDENCE_REF),
            "staticHash": HexBytes(STATIC_HASH),
            "writer": WRITER,
        }
        event_name = "EvidenceRecorded"
    else:
        function_name = "recordAccess"
        params = {
            "evidenceRef": HexBytes(EVIDENCE_REF),
            "officerRef": HexBytes(OFFICER_REF),
            "accessSessionRef": HexBytes(SESSION_REF),
        }
        args = {
            "evidenceRef": HexBytes(EVIDENCE_REF),
            "officerRef": HexBytes(OFFICER_REF),
            "accessSessionRef": HexBytes(SESSION_REF),
            "writer": WRITER,
        }
        event_name = "EvidenceAccessRecorded"
    event = {
        "address": CONTRACT,
        "blockNumber": 10,
        "transactionHash": HexBytes(TX_HASH),
        "args": args,
    }
    state = {
        "evidence": {"static_hash": STATIC_HASH, "writer": WRITER, "exists": True},
        "access": {"evidence_ref": EVIDENCE_REF, "officer_ref": OFFICER_REF, "writer": WRITER},
    }
    data: dict[str, Any] = {
        "tx": tx,
        "receipt": receipt,
        "block": {"timestamp": 1_786_000_000},
        "function_name": function_name,
        "params": params,
        "events": [event],
        "state": state,
    }
    eth = SimpleNamespace(
        block_number=12,
        get_transaction=lambda tx_hash: data["tx"],
        get_transaction_receipt=lambda tx_hash: data["receipt"],
        get_block=lambda number: data["block"],
    )
    events = SimpleNamespace()
    setattr(events, event_name, EventFactory(data["events"]))
    client = SimpleNamespace(
        validate_connection=lambda: None,
        settings=BlockchainClientSettings(
            provider_uri="http://127.0.0.1:8545",
            chain_id=20260720,
            contract_address=CONTRACT,
            artifact_path=Path("tests/fixtures/EvidenceRegistry.json"),
            confirmation_blocks=1,
        ),
        web3=SimpleNamespace(eth=eth),
        contract=SimpleNamespace(
            address=CONTRACT,
            events=events,
            decode_function_input=lambda value: (
                SimpleNamespace(fn_name=data["function_name"]),
                data["params"],
            ),
        ),
        get_evidence=lambda evidence_ref: data["state"]["evidence"],
        get_access_by_session=lambda session_ref: data["state"]["access"],
    )
    return TransactionVerifier(client), data


def test_successful_evidence_verification() -> None:
    verifier, _ = make_context()
    result = verifier.verify_evidence_transaction(TX_HASH.upper().replace("0X", "0x"))
    assert result.evidence_ref == EVIDENCE_REF
    assert result.static_hash == STATIC_HASH
    assert result.confirmations == 2


def test_successful_access_verification() -> None:
    verifier, _ = make_context("access")
    result = verifier.verify_access_transaction(TX_HASH)
    assert result.officer_ref == OFFICER_REF
    assert result.access_session_ref == SESSION_REF


def test_transaction_not_found() -> None:
    verifier, _ = make_context()

    def missing(tx_hash: str) -> None:
        raise TransactionNotFound("missing")

    verifier.client.web3.eth.get_transaction = missing
    with pytest.raises(TransactionVerificationError, match="transaction not found"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_failed_receipt() -> None:
    verifier, data = make_context()
    data["receipt"]["status"] = 0
    with pytest.raises(TransactionVerificationError, match="transaction failed"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_insufficient_confirmations() -> None:
    verifier, _ = make_context()
    verifier.client.web3.eth.block_number = 10
    with pytest.raises(TransactionVerificationError, match="insufficient confirmations"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_wrong_contract_target() -> None:
    verifier, data = make_context()
    data["tx"]["to"] = OTHER_CONTRACT
    with pytest.raises(TransactionVerificationError, match="configured contract"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_wrong_function() -> None:
    verifier, data = make_context()
    data["function_name"] = "recordAccess"
    with pytest.raises(TransactionVerificationError, match="did not call recordEvidence"):
        verifier.verify_evidence_transaction(TX_HASH)


@pytest.mark.parametrize("event_count", [0, 2])
def test_missing_or_duplicate_event(event_count: int) -> None:
    verifier, data = make_context()
    data["events"][:] = data["events"] * event_count
    with pytest.raises(TransactionVerificationError, match="expected exactly one"):
        verifier.verify_evidence_transaction(TX_HASH)


def mutate_event(mutator: Callable[[dict[str, Any]], None]) -> TransactionVerifier:
    verifier, data = make_context()
    mutator(data["events"][0])
    return verifier


def test_event_address_mismatch() -> None:
    verifier = mutate_event(lambda event: event.update(address=OTHER_CONTRACT))
    with pytest.raises(TransactionVerificationError, match="event contract address"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_event_receipt_block_mismatch() -> None:
    verifier = mutate_event(lambda event: event.update(blockNumber=11))
    with pytest.raises(TransactionVerificationError, match="event block number"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_event_receipt_transaction_hash_mismatch() -> None:
    verifier = mutate_event(lambda event: event.update(transactionHash=OTHER_TX_HASH))
    with pytest.raises(TransactionVerificationError, match="event transaction hash"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_input_event_mismatch() -> None:
    verifier = mutate_event(
        lambda event: event["args"].update(staticHash=HexBytes("0x" + "23" * 32))
    )
    with pytest.raises(TransactionVerificationError, match="event/input mismatch"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_writer_sender_mismatch() -> None:
    verifier = mutate_event(lambda event: event["args"].update(writer=OTHER_WRITER))
    with pytest.raises(TransactionVerificationError, match="writer does not match"):
        verifier.verify_evidence_transaction(TX_HASH)


def test_state_event_mismatch() -> None:
    verifier, data = make_context()
    data["state"]["evidence"]["static_hash"] = "0x" + "24" * 32
    with pytest.raises(TransactionVerificationError, match="state/event mismatch"):
        verifier.verify_evidence_transaction(TX_HASH)
