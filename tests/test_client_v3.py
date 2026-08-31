from pathlib import Path
from types import MethodType, SimpleNamespace
from unittest.mock import MagicMock

import pytest
from hexbytes import HexBytes

from blockchain_client import AccessAction, BlockchainClient, BlockchainClientSettings
from blockchain_client.client import geth_poa_middleware

EVIDENCE_REF = "0x" + "11" * 32
OFFICER_REF = "0x" + "22" * 32
SESSION_REF = "0x" + "33" * 32
WRITER = "0x" + "44" * 20
OCCURRED_AT = 1_700_000_000


def test_proof_of_authority_settings_install_poa_middleware() -> None:
    web3 = MagicMock()
    settings = BlockchainClientSettings(
        provider_uri="http://127.0.0.1:8545",
        chain_id=20_260_720,
        contract_address="0x" + "55" * 20,
        artifact_path=Path("tests/fixtures/EvidenceRegistryV3.json"),
        proof_of_authority=True,
    )

    BlockchainClient(settings, web3=web3)

    web3.middleware_onion.inject.assert_called_once_with(
        geth_poa_middleware,
        layer=0,
    )


def writable_client() -> tuple[BlockchainClient, MagicMock]:
    client = object.__new__(BlockchainClient)
    client.signer = SimpleNamespace(address=WRITER)
    client.nonce_manager = SimpleNamespace()
    record_access = MagicMock(return_value=SimpleNamespace())
    client.contract = SimpleNamespace(
        functions=SimpleNamespace(recordAccess=record_access)
    )
    client._send_contract_transaction = MagicMock(return_value="result")
    return client, record_access


@pytest.mark.parametrize("action", [AccessAction.VIEW, AccessAction.DOWNLOAD])
def test_record_access_serializes_v3_action_and_occurred_at(action: AccessAction) -> None:
    client, contract_call = writable_client()

    result = client.record_access(
        EVIDENCE_REF,
        OFFICER_REF,
        SESSION_REF,
        action,
        OCCURRED_AT,
    )

    assert result == "result"
    contract_call.assert_called_once_with(
        EVIDENCE_REF,
        OFFICER_REF,
        SESSION_REF,
        action.value,
        OCCURRED_AT,
    )
    expected = client._send_contract_transaction.call_args.args[2]
    assert expected["action"] == action.value
    assert expected["occurredAt"] == OCCURRED_AT


@pytest.mark.parametrize("action", [0, 1, 2, "VIEW", None])
def test_record_access_rejects_non_symbolic_action(action: object) -> None:
    client, contract_call = writable_client()

    with pytest.raises(ValueError, match="action must be AccessAction"):
        client.record_access(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            action,  # type: ignore[arg-type]
            OCCURRED_AT,
        )

    contract_call.assert_not_called()


@pytest.mark.parametrize("occurred_at", [0, -1, 2**64, True, 1.5, "1700000000"])
def test_record_access_rejects_invalid_occurred_at(occurred_at: object) -> None:
    client, contract_call = writable_client()

    with pytest.raises(ValueError, match="occurred_at"):
        client.record_access(
            EVIDENCE_REF,
            OFFICER_REF,
            SESSION_REF,
            AccessAction.VIEW,
            occurred_at,  # type: ignore[arg-type]
        )

    contract_call.assert_not_called()


def test_get_access_by_session_maps_v3_tuple() -> None:
    client = object.__new__(BlockchainClient)
    client.validate_connection = MethodType(lambda self: None, client)
    call = MagicMock(
        return_value=(
            HexBytes(EVIDENCE_REF),
            HexBytes(OFFICER_REF),
            AccessAction.DOWNLOAD.value,
            OCCURRED_AT,
            OCCURRED_AT + 30,
            WRITER,
        )
    )
    client.contract = SimpleNamespace(
        functions=SimpleNamespace(
            getAccessBySession=lambda session: SimpleNamespace(call=call)
        )
    )

    result = client.get_access_by_session(SESSION_REF)

    assert result == {
        "evidence_ref": EVIDENCE_REF,
        "officer_ref": OFFICER_REF,
        "action": AccessAction.DOWNLOAD,
        "occurred_at": OCCURRED_AT,
        "recorded_at": OCCURRED_AT + 30,
        "writer": WRITER,
    }
