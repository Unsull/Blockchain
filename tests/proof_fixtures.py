from __future__ import annotations

from datetime import UTC, datetime

from blockchain_client.proof_models import (
    SCHEMA_VERSION,
    ChainMetadata,
    EvidenceTransactionProof,
    TransactionMetadata,
    VerificationChecks,
)

TX_HASH = "0x" + "ab" * 32
BLOCK_HASH = "0x" + "cd" * 32
EVIDENCE_REF = "0x" + "11" * 32
EVIDENCE_HASH = "0x" + "22" * 32
UPLOADER_REF = "0x" + "77" * 32
WRITER = "0x" + "33" * 20
CONTRACT = "0x" + "44" * 20


def successful_checks() -> VerificationChecks:
    return VerificationChecks(True, True, True, True, True, True, True, True, True)


def evidence_proof() -> EvidenceTransactionProof:
    return EvidenceTransactionProof(
        schema_version=SCHEMA_VERSION,
        generated_at_utc=datetime(2026, 8, 6, tzinfo=UTC),
        operation="recordEvidence",
        verification_status="verified",
        chain=ChainMetadata(20260720, CONTRACT.upper().replace("0X", "0x")),
        transaction=TransactionMetadata(
            tx_hash=TX_HASH.upper().replace("0X", "0x"),
            sender=WRITER.upper().replace("0X", "0x"),
            target=CONTRACT.upper().replace("0X", "0x"),
            receipt_status=1,
            block_number=100,
            block_hash=BLOCK_HASH.upper().replace("0X", "0x"),
            block_timestamp_utc=datetime(2026, 8, 6, tzinfo=UTC),
            gas_used=75000,
            effective_gas_price=None,
            confirmations=2,
        ),
        function_name="recordEvidence",
        evidence_ref=EVIDENCE_REF.upper().replace("0X", "0x"),
        evidence_hash=EVIDENCE_HASH.upper().replace("0X", "0x"),
        uploader_ref=UPLOADER_REF.upper().replace("0X", "0x"),
        writer_address=WRITER.upper().replace("0X", "0x"),
        checks=successful_checks(),
    )
