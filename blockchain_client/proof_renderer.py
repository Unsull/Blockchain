"""Deterministic JSON and Markdown rendering for transaction proofs."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from blockchain_client.proof_models import AccessTransactionProof, TransactionProof


def proof_to_json(proof: TransactionProof, indent: int = 2) -> str:
    return json.dumps(proof.to_dict(), indent=indent, ensure_ascii=True) + "\n"


def proof_to_markdown(proof: TransactionProof) -> str:
    transaction = proof.transaction
    summary = [
        "# Blockchain Transaction Verification Proof",
        "",
        "## Summary",
        "",
        f"- Operation: `{proof.operation}`",
        f"- Verification status: `{proof.verification_status}`",
        f"- Chain ID: `{proof.chain.chain_id}`",
        f"- Contract address: `{proof.chain.contract_address}`",
        f"- Transaction hash: `{transaction.tx_hash}`",
        f"- Sender: `{transaction.sender}`",
        f"- Target: `{transaction.target}`",
        f"- Receipt status: `{transaction.receipt_status}`",
        f"- Block number: `{transaction.block_number}`",
        f"- Block hash: `{transaction.block_hash}`",
        f"- Block timestamp UTC: `{transaction.to_dict()['block_timestamp_utc']}`",
        f"- Confirmations: `{transaction.confirmations}`",
        f"- Gas used: `{transaction.gas_used}`",
    ]
    if transaction.effective_gas_price is not None:
        summary.append(f"- Effective gas price: `{transaction.effective_gas_price}`")

    decoded = [
        "",
        "## Decoded Contract Call",
        "",
        f"- Function: `{proof.function_name}`",
        f"- Evidence reference: `{proof.evidence_ref}`",
    ]
    if isinstance(proof, AccessTransactionProof):
        decoded.extend(
            [
                f"- Officer reference: `{proof.officer_ref}`",
                f"- Access session reference: `{proof.access_session_ref}`",
            ]
        )
    else:
        decoded.extend(
            [
                f"- Evidence hash: `{proof.evidence_hash}`",
                f"- Uploader reference: `{proof.uploader_ref}`",
            ]
        )

    labels = {
        "transaction_found": "Transaction found",
        "receipt_successful": "Receipt status successful",
        "contract_target_matches": "Contract target matches",
        "function_matches": "Function matches",
        "input_event_matches": "Input matches event",
        "event_receipt_matches": "Event metadata matches receipt",
        "writer_sender_matches": "Writer matches sender",
        "event_state_matches": "Event matches contract state",
        "confirmations_sufficient": "Confirmations sufficient",
    }
    checks = ["", "## Verification Checks", "", "| Check | Result |", "|---|---|"]
    for key, value in proof.checks.to_dict().items():
        checks.append(f"| {labels[key]} | {'PASS' if value else 'FAIL'} |")

    footer = [
        "",
        "## Interpretation",
        "",
        "- This verifies a specific transaction on the configured integration/staging chain.",
        "- It is not legal certification.",
        "- Opaque bytes32 references do not reveal real identities by themselves.",
        (
            "- Verification is limited to the configured chain, contract, receipt, event, "
            "and state at generation time."
        ),
        "",
        "## Reproduction Information",
        "",
        f"- Schema version: `{proof.schema_version}`",
        f"- UTC generation time: `{proof.to_dict()['generated_at_utc']}`",
        f"- Chain ID: `{proof.chain.chain_id}`",
        f"- Contract address: `{proof.chain.contract_address}`",
        "",
    ]
    return "\n".join(summary + decoded + checks + footer)


def _atomic_write(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def write_json_proof(proof: TransactionProof, path: str | Path) -> None:
    _atomic_write(proof_to_json(proof), Path(path))


def write_markdown_proof(proof: TransactionProof, path: str | Path) -> None:
    _atomic_write(proof_to_markdown(proof), Path(path))
