"""Signed transaction client for EvidenceRegistry."""

from datetime import UTC, datetime
from typing import Any, cast

from eth_account import Account
from web3 import Web3

from blockchain_client.artifacts import load_contract_abi
from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import ContractConnectionError, TransactionSubmissionError
from blockchain_client.models import TransactionResult
from blockchain_client.references import normalize_bytes32


class BlockchainClient:
    """Client that submits signed raw transactions to EvidenceRegistry."""

    def __init__(self, settings: BlockchainClientSettings, web3: Web3 | None = None) -> None:
        settings.validate()
        self.settings = settings
        self.web3 = web3 or Web3(Web3.HTTPProvider(settings.provider_uri))
        self.account = Account.from_key(settings.signer_private_key)
        self.abi = load_contract_abi(settings.artifact_path)
        self.contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(settings.contract_address),
            abi=self.abi,
        )

    def validate_connection(self) -> None:
        """Fail fast when provider, chain ID, or deployed bytecode is invalid."""

        if not self.web3.is_connected():
            raise ContractConnectionError("provider is not connected")
        chain_id = self.web3.eth.chain_id
        if chain_id != self.settings.chain_id:
            raise ContractConnectionError(
                f"chain ID mismatch: expected {self.settings.chain_id}, got {chain_id}"
            )
        bytecode = self.web3.eth.get_code(self.contract.address)
        if bytecode in (b"", "0x", None):
            raise ContractConnectionError("no deployed bytecode at contract address")

    def record_evidence(self, evidence_ref: str, static_hash: str) -> TransactionResult:
        """Record a static evidence hash using opaque bytes32 references."""

        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        static = normalize_bytes32(static_hash, "static_hash")
        function = self.contract.functions.recordEvidence(evidence, static)
        return self._send_contract_transaction(function, "EvidenceRecorded")

    def record_access(
        self,
        evidence_ref: str,
        officer_ref: str,
        access_session_ref: str,
    ) -> TransactionResult:
        """Record an access session using opaque bytes32 references."""

        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        officer = normalize_bytes32(officer_ref, "officer_ref")
        session = normalize_bytes32(access_session_ref, "access_session_ref")
        function = self.contract.functions.recordAccess(evidence, officer, session)
        return self._send_contract_transaction(function, "EvidenceAccessRecorded")

    def get_evidence(self, evidence_ref: str) -> dict[str, Any]:
        """Query an evidence record from contract state."""

        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        static_hash, recorded_at, writer, exists = (
            self.contract.functions.getEvidence(evidence).call()
        )
        return {
            "static_hash": static_hash.hex(),
            "recorded_at": recorded_at,
            "writer": writer,
            "exists": exists,
        }

    def get_access_by_session(self, access_session_ref: str) -> dict[str, Any]:
        """Query an access record by access session reference."""

        session = normalize_bytes32(access_session_ref, "access_session_ref")
        evidence_ref, officer_ref, recorded_at, writer = (
            self.contract.functions.getAccessBySession(session).call()
        )
        return {
            "evidence_ref": evidence_ref.hex(),
            "officer_ref": officer_ref.hex(),
            "recorded_at": recorded_at,
            "writer": writer,
        }

    def _send_contract_transaction(
        self,
        function: Any,
        expected_event_name: str,
    ) -> TransactionResult:
        self.validate_connection()
        try:
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            transaction = function.build_transaction(
                {
                    "from": self.account.address,
                    "chainId": self.settings.chain_id,
                    "nonce": nonce,
                }
            )
            gas_estimate = self.web3.eth.estimate_gas(transaction)
            transaction["gas"] = int(gas_estimate * 1.2)
            signed = self.account.sign_transaction(transaction)
            raw_transaction = getattr(signed, "raw_transaction", signed.rawTransaction)
            tx_hash = self.web3.eth.send_raw_transaction(raw_transaction)
            receipt = cast(
                Any,
                self.web3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=self.settings.request_timeout_seconds,
                ),
            )
        except Exception as exc:
            raise TransactionSubmissionError("failed to submit signed transaction") from exc

        if receipt["status"] != 1:
            raise TransactionSubmissionError("transaction receipt status is 0")

        event = self._decode_expected_event(receipt, expected_event_name)
        block = cast(Any, self.web3.eth.get_block(receipt["blockNumber"]))
        confirmations = max(self.web3.eth.block_number - receipt["blockNumber"], 0)
        return TransactionResult(
            tx_hash=receipt["transactionHash"].hex(),
            block_number=receipt["blockNumber"],
            block_timestamp=datetime.fromtimestamp(block["timestamp"], tz=UTC),
            contract_address=self.contract.address,
            chain_id=self.settings.chain_id,
            confirmations=confirmations,
            event=event,
        )

    def _decode_expected_event(self, receipt: Any, event_name: str) -> dict[str, Any]:
        event_class = getattr(self.contract.events, event_name)
        decoded = event_class().process_receipt(receipt)
        if not decoded:
            raise TransactionSubmissionError(f"expected event missing: {event_name}")
        return dict(decoded[0]["args"])
