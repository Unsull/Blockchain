"""Transaction verifier for historical EvidenceRegistry transactions."""

from datetime import UTC, datetime
from typing import Any, cast

from eth_typing import HexStr
from web3.exceptions import TransactionNotFound

from blockchain_client.client import BlockchainClient
from blockchain_client.exceptions import TransactionVerificationError
from blockchain_client.models import VerifiedAccess, VerifiedEvidence
from blockchain_client.references import normalize_tx_hash


class TransactionVerifier:
    """Verify transaction input, receipt, event payload, and contract state."""

    def __init__(self, client: BlockchainClient) -> None:
        self.client = client

    def verify_evidence_transaction(self, tx_hash: str) -> VerifiedEvidence:
        """Verify a recordEvidence transaction."""

        normalized = normalize_tx_hash(tx_hash)
        tx, receipt, block = self._load_successful_transaction(normalized)
        self._assert_contract_target(tx)
        function, params = self.client.contract.decode_function_input(tx.input)
        if function.fn_name != "recordEvidence":
            raise TransactionVerificationError("transaction did not call recordEvidence")

        event = self._single_event(receipt, "EvidenceRecorded")
        evidence_ref = params["evidenceRef"].hex()
        static_hash = params["staticHash"].hex()
        if event["evidenceRef"].hex() != evidence_ref or event["staticHash"].hex() != static_hash:
            raise TransactionVerificationError("event/input mismatch")

        state = self.client.get_evidence(evidence_ref)
        if state["static_hash"] != static_hash:
            raise TransactionVerificationError("state/event mismatch")

        return VerifiedEvidence(
            evidence_ref=evidence_ref,
            static_hash=static_hash,
            tx_hash=normalized,
            block_number=receipt.blockNumber,
            block_timestamp=datetime.fromtimestamp(block["timestamp"], tz=UTC),
            writer=event["writer"],
            confirmations=self._confirmations(receipt["blockNumber"]),
            status="verified",
        )

    def verify_access_transaction(self, tx_hash: str) -> VerifiedAccess:
        """Verify a recordAccess transaction."""

        normalized = normalize_tx_hash(tx_hash)
        tx, receipt, block = self._load_successful_transaction(normalized)
        self._assert_contract_target(tx)
        function, params = self.client.contract.decode_function_input(tx.input)
        if function.fn_name != "recordAccess":
            raise TransactionVerificationError("transaction did not call recordAccess")

        event = self._single_event(receipt, "EvidenceAccessRecorded")
        evidence_ref = params["evidenceRef"].hex()
        officer_ref = params["officerRef"].hex()
        session_ref = params["accessSessionRef"].hex()
        if (
            event["evidenceRef"].hex() != evidence_ref
            or event["officerRef"].hex() != officer_ref
            or event["accessSessionRef"].hex() != session_ref
        ):
            raise TransactionVerificationError("event/input mismatch")

        state = self.client.get_access_by_session(session_ref)
        if state["evidence_ref"] != evidence_ref or state["officer_ref"] != officer_ref:
            raise TransactionVerificationError("state/event mismatch")

        return VerifiedAccess(
            evidence_ref=evidence_ref,
            officer_ref=officer_ref,
            access_session_ref=session_ref,
            tx_hash=normalized,
            block_number=receipt.blockNumber,
            block_timestamp=datetime.fromtimestamp(block["timestamp"], tz=UTC),
            writer=event["writer"],
            confirmations=self._confirmations(receipt["blockNumber"]),
            status="verified",
        )

    def _load_successful_transaction(self, tx_hash: str) -> tuple[Any, Any, Any]:
        try:
            tx = cast(Any, self.client.web3.eth.get_transaction(HexStr(tx_hash)))
            receipt = cast(Any, self.client.web3.eth.get_transaction_receipt(HexStr(tx_hash)))
        except TransactionNotFound as exc:
            raise TransactionVerificationError("transaction not found") from exc
        if receipt["status"] != 1:
            raise TransactionVerificationError("transaction failed")
        block = cast(Any, self.client.web3.eth.get_block(receipt["blockNumber"]))
        if self._confirmations(receipt["blockNumber"]) < self.client.settings.confirmation_blocks:
            raise TransactionVerificationError("insufficient confirmations")
        return tx, receipt, block

    def _assert_contract_target(self, tx: Any) -> None:
        if tx["to"].lower() != self.client.contract.address.lower():
            raise TransactionVerificationError("transaction target is not the configured contract")

    def _single_event(self, receipt: Any, event_name: str) -> Any:
        event_class = getattr(self.client.contract.events, event_name)
        decoded = event_class().process_receipt(receipt)
        if len(decoded) != 1:
            raise TransactionVerificationError(f"expected exactly one {event_name} event")
        return decoded[0]["args"]

    def _confirmations(self, block_number: int) -> int:
        return max(self.client.web3.eth.block_number - block_number, 0)
