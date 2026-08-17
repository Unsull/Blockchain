"""Build structured proofs after TransactionVerifier completes successfully."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, cast

from eth_typing import HexStr

from blockchain_client.client import BlockchainClient
from blockchain_client.proof_models import (
    SCHEMA_VERSION,
    AccessTransactionProof,
    ChainMetadata,
    EvidenceTransactionProof,
    TransactionMetadata,
    VerificationChecks,
)
from blockchain_client.references import bytes32_to_hex, normalize_tx_hash
from blockchain_client.transaction_verifier import TransactionVerifier


class TransactionProofBuilder:
    def __init__(
        self,
        client: BlockchainClient,
        verifier: TransactionVerifier | None = None,
    ) -> None:
        self.client = client
        self.verifier = verifier or TransactionVerifier(client)

    def build_evidence_proof(self, tx_hash: str) -> EvidenceTransactionProof:
        verified = self.verifier.verify_evidence_transaction(tx_hash)
        tx, receipt, block, function_name, params = self._load_metadata(tx_hash)
        return EvidenceTransactionProof(
            schema_version=SCHEMA_VERSION,
            generated_at_utc=datetime.now(UTC),
            operation="recordEvidence",
            verification_status="verified",
            chain=self._chain(),
            transaction=self._transaction(tx, receipt, block, verified.confirmations),
            function_name=function_name,
            evidence_ref=bytes32_to_hex(params["evidenceRef"]),
            evidence_hash=bytes32_to_hex(params["evidenceHash"]),
            uploader_ref=bytes32_to_hex(params["uploaderRef"]),
            writer_address=verified.writer,
            checks=self._successful_checks(),
        )

    def build_access_proof(self, tx_hash: str) -> AccessTransactionProof:
        verified = self.verifier.verify_access_transaction(tx_hash)
        tx, receipt, block, function_name, params = self._load_metadata(tx_hash)
        return AccessTransactionProof(
            schema_version=SCHEMA_VERSION,
            generated_at_utc=datetime.now(UTC),
            operation="recordAccess",
            verification_status="verified",
            chain=self._chain(),
            transaction=self._transaction(tx, receipt, block, verified.confirmations),
            function_name=function_name,
            evidence_ref=bytes32_to_hex(params["evidenceRef"]),
            officer_ref=bytes32_to_hex(params["officerRef"]),
            access_session_ref=bytes32_to_hex(params["accessSessionRef"]),
            writer_address=verified.writer,
            checks=self._successful_checks(),
        )

    def _load_metadata(self, tx_hash: str) -> tuple[Any, Any, Any, str, dict[str, Any]]:
        normalized = normalize_tx_hash(tx_hash)
        tx = cast(Any, self.client.web3.eth.get_transaction(HexStr(normalized)))
        receipt = cast(Any, self.client.web3.eth.get_transaction_receipt(HexStr(normalized)))
        block = cast(Any, self.client.web3.eth.get_block(receipt["blockNumber"]))
        function, params = self.client.contract.decode_function_input(tx["input"])
        return tx, receipt, block, function.fn_name, cast(dict[str, Any], params)

    def _chain(self) -> ChainMetadata:
        return ChainMetadata(
            chain_id=self.client.settings.chain_id,
            contract_address=self.client.contract.address,
        )

    def _transaction(
        self, tx: Any, receipt: Any, block: Any, confirmations: int
    ) -> TransactionMetadata:
        block_hash = block["hash"].hex() if hasattr(block["hash"], "hex") else str(block["hash"])
        tx_hash = (
            receipt["transactionHash"].hex()
            if hasattr(receipt["transactionHash"], "hex")
            else str(receipt["transactionHash"])
        )
        return TransactionMetadata(
            tx_hash=tx_hash,
            sender=tx["from"],
            target=tx["to"],
            receipt_status=receipt["status"],
            block_number=receipt["blockNumber"],
            block_hash=block_hash,
            block_timestamp_utc=datetime.fromtimestamp(block["timestamp"], tz=UTC),
            gas_used=receipt["gasUsed"],
            effective_gas_price=receipt.get("effectiveGasPrice"),
            confirmations=confirmations,
        )

    @staticmethod
    def _successful_checks() -> VerificationChecks:
        return VerificationChecks(
            transaction_found=True,
            receipt_successful=True,
            contract_target_matches=True,
            function_matches=True,
            input_event_matches=True,
            event_receipt_matches=True,
            writer_sender_matches=True,
            event_state_matches=True,
            confirmations_sufficient=True,
        )
