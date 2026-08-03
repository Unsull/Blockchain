"""Signed transaction client for EvidenceRegistry."""

from datetime import UTC, datetime
from time import monotonic, sleep
from typing import Any, cast

from web3 import Web3
from web3.exceptions import TimeExhausted
from web3.middleware.geth_poa import geth_poa_middleware

from blockchain_client.artifacts import load_contract_abi
from blockchain_client.config import BlockchainClientSettings
from blockchain_client.exceptions import (
    ChainIdMismatchError,
    ContractConnectionError,
    ContractNotDeployedError,
    EventDecodeError,
    EventValidationError,
    NonceError,
    TransactionBuildError,
    TransactionConfirmationTimeoutError,
    TransactionRevertedError,
    TransactionSigningError,
    TransactionSubmissionError,
    TransactionTimeoutError,
)
from blockchain_client.models import BlockchainHealth, TransactionResult
from blockchain_client.nonce import NonceManager
from blockchain_client.references import bytes32_to_hex, normalize_bytes32
from blockchain_client.signer import LocalPrivateKeySigner, TransactionSigner


class BlockchainClient:
    """Client that submits signed raw transactions to EvidenceRegistry."""

    def __init__(
        self,
        settings: BlockchainClientSettings,
        signer: TransactionSigner | None = None,
        web3: Web3 | None = None,
    ) -> None:
        settings.validate()
        self.settings = settings
        self.web3 = web3 or Web3(Web3.HTTPProvider(settings.provider_uri))
        if settings.proof_of_authority:
            self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if signer is None:
            if not settings.signer_private_key:
                raise TransactionBuildError("signer is required when signer_private_key is not set")
            signer = LocalPrivateKeySigner(settings.signer_private_key)
        self.signer = signer
        self.nonce_manager = NonceManager(self.web3, self.signer.address)
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
            raise ChainIdMismatchError(
                f"chain ID mismatch: expected {self.settings.chain_id}, got {chain_id}"
            )
        bytecode = self.web3.eth.get_code(self.contract.address)
        if bytecode in (b"", "0x", None):
            raise ContractNotDeployedError("no deployed bytecode at contract address")

    def health_check(self) -> BlockchainHealth:
        """Return provider, chain, and contract deployment health without exposing secrets."""

        connected = self.web3.is_connected()
        chain_id: int | None = None
        latest_block: int | None = None
        deployed = False
        if connected:
            chain_id = self.web3.eth.chain_id
            latest_block = self.web3.eth.block_number
            deployed = self.web3.eth.get_code(self.contract.address) not in (b"", "0x", None)
        return BlockchainHealth(
            connected=connected,
            chain_id=chain_id,
            latest_block=latest_block,
            contract_address=self.contract.address,
            contract_deployed=deployed,
        )

    def record_evidence(self, evidence_ref: str, static_hash: str) -> TransactionResult:
        """Record a static evidence hash using opaque bytes32 references."""

        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        static = normalize_bytes32(static_hash, "static_hash")
        function = self.contract.functions.recordEvidence(evidence, static)
        return self._send_contract_transaction(
            function,
            "EvidenceRecorded",
            {"evidenceRef": evidence, "staticHash": static, "writer": self.signer.address},
        )

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
        return self._send_contract_transaction(
            function,
            "EvidenceAccessRecorded",
            {
                "evidenceRef": evidence,
                "officerRef": officer,
                "accessSessionRef": session,
                "writer": self.signer.address,
            },
        )

    def get_evidence(self, evidence_ref: str) -> dict[str, Any]:
        """Query an evidence record from contract state."""

        self.validate_connection()
        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        static_hash, recorded_at, writer, exists = (
            self.contract.functions.getEvidence(evidence).call()
        )
        return {
            "static_hash": bytes32_to_hex(static_hash),
            "recorded_at": recorded_at,
            "writer": writer,
            "exists": exists,
        }

    def get_access_by_session(self, access_session_ref: str) -> dict[str, Any]:
        """Query an access record by access session reference."""

        self.validate_connection()
        session = normalize_bytes32(access_session_ref, "access_session_ref")
        evidence_ref, officer_ref, recorded_at, writer = (
            self.contract.functions.getAccessBySession(session).call()
        )
        return {
            "evidence_ref": bytes32_to_hex(evidence_ref),
            "officer_ref": bytes32_to_hex(officer_ref),
            "recorded_at": recorded_at,
            "writer": writer,
        }

    def evidence_exists(self, evidence_ref: str) -> bool:
        """Return whether an evidence reference exists."""

        self.validate_connection()
        evidence = normalize_bytes32(evidence_ref, "evidence_ref")
        return bool(self.contract.functions.evidenceExists(evidence).call())

    def access_session_exists(self, access_session_ref: str) -> bool:
        """Return whether an access session reference exists."""

        self.validate_connection()
        session = normalize_bytes32(access_session_ref, "access_session_ref")
        return bool(self.contract.functions.accessSessionExists(session).call())

    def _send_contract_transaction(
        self,
        function: Any,
        expected_event_name: str,
        expected_args: dict[str, Any],
    ) -> TransactionResult:
        self.validate_connection()
        try:
            nonce = self.nonce_manager.next_nonce()
            transaction = function.build_transaction(
                {"from": self.signer.address, "chainId": self.settings.chain_id, "nonce": nonce}
            )
        except NonceError:
            raise
        except Exception as exc:
            raise TransactionBuildError("failed to build transaction") from exc

        try:
            gas_estimate = self.web3.eth.estimate_gas(transaction)
            transaction["gas"] = int(gas_estimate * self.settings.gas_estimate_multiplier)
            self._apply_fee_settings(transaction)
        except Exception as exc:
            self.nonce_manager.reset()
            raise TransactionBuildError("failed to estimate gas or apply fees") from exc

        try:
            raw_transaction = self.signer.sign_transaction(transaction)
        except TransactionSigningError:
            self.nonce_manager.reset()
            raise
        except Exception as exc:
            self.nonce_manager.reset()
            raise TransactionSigningError("failed to sign transaction") from exc

        try:
            tx_hash = self.web3.eth.send_raw_transaction(raw_transaction)
        except Exception as exc:
            self.nonce_manager.reset()
            if self._is_nonce_error(exc):
                raise NonceError("nonce conflict while submitting transaction") from exc
            raise TransactionSubmissionError("failed to submit signed transaction") from exc

        try:
            receipt = cast(
                Any,
                self.web3.eth.wait_for_transaction_receipt(
                    tx_hash,
                    timeout=self.settings.request_timeout_seconds,
                ),
            )
        except TimeExhausted as exc:
            raise TransactionTimeoutError("timed out waiting for transaction receipt") from exc

        if receipt["status"] != 1:
            raise TransactionRevertedError("transaction receipt status is 0")

        event = self._decode_and_validate_event(
            receipt,
            expected_event_name,
            expected_args,
        )
        confirmations = self._wait_for_confirmations(receipt["blockNumber"])
        block = cast(Any, self.web3.eth.get_block(receipt["blockNumber"]))
        return TransactionResult(
            tx_hash=receipt["transactionHash"].hex(),
            block_number=receipt["blockNumber"],
            block_timestamp=datetime.fromtimestamp(block["timestamp"], tz=UTC),
            contract_address=self.contract.address,
            chain_id=self.settings.chain_id,
            confirmations=confirmations,
            event=event,
        )

    def _apply_fee_settings(self, transaction: dict[str, Any]) -> None:
        if self.settings.legacy_gas_price is not None:
            transaction["gasPrice"] = self.settings.legacy_gas_price
            return

        latest_block = self.web3.eth.get_block("latest")
        base_fee = latest_block.get("baseFeePerGas")
        if base_fee is None:
            transaction["gasPrice"] = self.settings.legacy_gas_price or self.web3.eth.gas_price
            return

        priority_fee = self.settings.max_priority_fee_per_gas
        if priority_fee is None:
            priority_fee = self.web3.eth.max_priority_fee
        max_fee = self.settings.max_fee_per_gas
        if max_fee is None:
            max_fee = int(base_fee) * 2 + int(priority_fee)
        transaction["maxPriorityFeePerGas"] = priority_fee
        transaction["maxFeePerGas"] = max_fee

    def _wait_for_confirmations(self, block_number: int) -> int:
        if self.settings.confirmation_blocks == 0:
            return max(self.web3.eth.block_number - block_number, 0)
        target_block = block_number + self.settings.confirmation_blocks
        deadline = monotonic() + self.settings.confirmation_timeout_seconds
        while monotonic() < deadline:
            current_block = self.web3.eth.block_number
            if current_block >= target_block:
                return current_block - block_number
            sleep(self.settings.confirmation_poll_interval_seconds)
        raise TransactionConfirmationTimeoutError("timed out waiting for confirmations")

    def _decode_and_validate_event(
        self,
        receipt: Any,
        event_name: str,
        expected_args: dict[str, Any],
    ) -> dict[str, Any]:
        event_class = getattr(self.contract.events, event_name)
        decoded = event_class().process_receipt(receipt)
        if len(decoded) != 1:
            raise EventDecodeError(f"expected exactly one {event_name} event")
        event = decoded[0]
        if event["address"].lower() != self.contract.address.lower():
            raise EventValidationError("event contract address mismatch")
        if event["blockNumber"] != receipt["blockNumber"]:
            raise EventValidationError("event block number mismatch")
        if event["transactionHash"] != receipt["transactionHash"]:
            raise EventValidationError("event transaction hash mismatch")

        args = dict(event["args"])
        for key, expected_value in expected_args.items():
            actual_value = args[key]
            if key.endswith("Ref") or key == "staticHash":
                if bytes32_to_hex(actual_value) != bytes32_to_hex(expected_value):
                    raise EventValidationError(f"event argument mismatch: {key}")
            elif key == "writer":
                if actual_value.lower() != str(expected_value).lower():
                    raise EventValidationError("event writer mismatch")
            elif actual_value != expected_value:
                raise EventValidationError(f"event argument mismatch: {key}")
        canonical_args = dict(args)
        for key in ("evidenceRef", "staticHash", "officerRef", "accessSessionRef"):
            if key in canonical_args:
                canonical_args[key] = bytes32_to_hex(canonical_args[key])
        return canonical_args

    def _is_nonce_error(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return "nonce too low" in message or "replacement transaction underpriced" in message
