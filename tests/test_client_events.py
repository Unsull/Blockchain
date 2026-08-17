from __future__ import annotations

from types import MethodType, SimpleNamespace
from typing import Any

import pytest
from hexbytes import HexBytes

from blockchain_client.client import BlockchainClient
from blockchain_client.exceptions import EventValidationError, ReferenceValidationError
from blockchain_client.models import EvidenceAccessEvent, EvidenceRecordedEvent

CONTRACT = "0x" + "44" * 20
OTHER_CONTRACT = "0x" + "45" * 20
WRITER = "0x" + "33" * 20
EVIDENCE_REF = "0x" + "11" * 32
EVIDENCE_HASH = "0x" + "22" * 32
UPLOADER_REF = "0x" + "77" * 32
OFFICER_REF = "0x" + "55" * 32
SESSION_REF = "0x" + "66" * 32


class EventLogs:
    def __init__(self, logs: list[dict[str, Any]]) -> None:
        self.logs = logs
        self.queries: list[dict[str, Any]] = []

    def __call__(self) -> EventLogs:
        return self

    def get_logs(self, **kwargs: Any) -> list[dict[str, Any]]:
        self.queries.append(kwargs)
        return self.logs


def evidence_log(*, address: str = CONTRACT) -> dict[str, Any]:
    return {
        "address": address,
        "args": {
            "evidenceRef": HexBytes(EVIDENCE_REF),
            "evidenceHash": HexBytes(EVIDENCE_HASH),
            "uploaderRef": HexBytes(UPLOADER_REF),
            "recordedAt": 1_700_000_000,
            "writer": WRITER,
        },
        "transactionHash": HexBytes("0x" + "ab" * 32),
        "blockNumber": 10,
        "transactionIndex": 2,
        "logIndex": 3,
    }


def access_log(
    *,
    block_number: int = 11,
    transaction_index: int = 1,
    log_index: int = 0,
    session_ref: str = SESSION_REF,
    address: str = CONTRACT,
) -> dict[str, Any]:
    return {
        "address": address,
        "args": {
            "evidenceRef": HexBytes(EVIDENCE_REF),
            "officerRef": HexBytes(OFFICER_REF),
            "accessSessionRef": HexBytes(session_ref),
            "recordedAt": 1_700_000_100,
            "writer": WRITER,
        },
        "transactionHash": HexBytes("0x" + f"{block_number:064x}"),
        "blockNumber": block_number,
        "transactionIndex": transaction_index,
        "logIndex": log_index,
    }


def make_client(
    *,
    evidence_logs: list[dict[str, Any]] | None = None,
    access_logs: list[dict[str, Any]] | None = None,
) -> tuple[BlockchainClient, EventLogs, EventLogs, list[str]]:
    client = object.__new__(BlockchainClient)
    validations: list[str] = []

    def validate_connection(self: BlockchainClient) -> None:
        validations.append("validated")

    recorded = EventLogs(evidence_logs or [])
    accessed = EventLogs(access_logs or [])
    client.validate_connection = MethodType(validate_connection, client)
    client.contract = SimpleNamespace(
        address=CONTRACT,
        events=SimpleNamespace(
            EvidenceRecorded=recorded,
            EvidenceAccessRecorded=accessed,
        ),
    )
    return client, recorded, accessed, validations


def test_get_evidence_record_event_found() -> None:
    client, recorded, _, validations = make_client(evidence_logs=[evidence_log()])

    event = client.get_evidence_record_event(EVIDENCE_REF, 5, 20)

    assert isinstance(event, EvidenceRecordedEvent)
    assert event.evidence_ref == EVIDENCE_REF
    assert event.evidence_hash == EVIDENCE_HASH
    assert event.uploader_ref == UPLOADER_REF
    assert event.tx_hash == "0x" + "ab" * 32
    assert validations == ["validated"]
    assert recorded.queries == [
        {
            "argument_filters": {"evidenceRef": EVIDENCE_REF},
            "fromBlock": 5,
            "toBlock": 20,
        }
    ]


def test_get_evidence_record_event_absent() -> None:
    client, _, _, _ = make_client()
    assert client.get_evidence_record_event(EVIDENCE_REF) is None


def test_get_evidence_record_event_rejects_duplicates() -> None:
    client, _, _, _ = make_client(evidence_logs=[evidence_log(), evidence_log()])
    with pytest.raises(EventValidationError, match="at most one EvidenceRecorded"):
        client.get_evidence_record_event(EVIDENCE_REF)


def test_list_access_events_empty() -> None:
    client, _, _, _ = make_client()
    assert client.list_access_events(EVIDENCE_REF) == []


def test_list_access_events_are_sorted_by_chain_position() -> None:
    logs = [
        access_log(block_number=12, transaction_index=0, log_index=0),
        access_log(block_number=11, transaction_index=2, log_index=1),
        access_log(block_number=11, transaction_index=1, log_index=4),
    ]
    client, _, _, _ = make_client(access_logs=logs)

    events = client.list_access_events(EVIDENCE_REF)

    assert all(isinstance(event, EvidenceAccessEvent) for event in events)
    assert [
        (event.block_number, event.transaction_index, event.log_index)
        for event in events
    ] == [(11, 1, 4), (11, 2, 1), (12, 0, 0)]
    assert all(event.access_session_ref == SESSION_REF for event in events)


def test_get_access_event_by_session_found() -> None:
    client, _, accessed, _ = make_client(access_logs=[access_log()])

    event = client.get_access_event_by_session(SESSION_REF)

    assert isinstance(event, EvidenceAccessEvent)
    assert event.access_session_ref == SESSION_REF
    assert accessed.queries[0]["argument_filters"] == {
        "accessSessionRef": SESSION_REF
    }


def test_get_access_event_by_session_absent() -> None:
    client, _, _, _ = make_client()
    assert client.get_access_event_by_session(SESSION_REF) is None


def test_get_access_event_by_session_rejects_duplicates() -> None:
    client, _, _, _ = make_client(access_logs=[access_log(), access_log()])
    with pytest.raises(EventValidationError, match="at most one EvidenceAccessRecorded"):
        client.get_access_event_by_session(SESSION_REF)


@pytest.mark.parametrize(
    "reader",
    [
        lambda client: client.get_evidence_record_event("0x01"),
        lambda client: client.list_access_events("0x01"),
        lambda client: client.get_access_event_by_session("0x01"),
    ],
)
def test_event_readers_reject_invalid_bytes32(reader: Any) -> None:
    client, _, _, _ = make_client()
    with pytest.raises(ReferenceValidationError):
        reader(client)


def test_event_reader_rejects_wrong_contract_address() -> None:
    client, _, _, _ = make_client(evidence_logs=[evidence_log(address=OTHER_CONTRACT)])
    with pytest.raises(EventValidationError, match="event contract address mismatch"):
        client.get_evidence_record_event(EVIDENCE_REF)
