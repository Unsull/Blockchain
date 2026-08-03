from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from uuid import uuid4

from blockchain_client import BlockchainClient, BlockchainClientSettings
from blockchain_client.transaction_verifier import TransactionVerifier

ROOT = Path(__file__).resolve().parents[3]


def to_bytes32(value: str) -> str:
    return "0x" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def run(command: list[str], env: dict[str, str]) -> None:
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def main() -> None:
    rpc_url = os.environ["RPC_URL"]
    chain_id = int(os.environ["CHAIN_ID"])
    contract_address = os.environ["CONTRACT_ADDRESS"]
    writer_key = os.environ["WRITER_PRIVATE_KEY"]
    artifact_path = Path(
        os.getenv("ARTIFACT_PATH", "out/EvidenceRegistry.sol/EvidenceRegistry.json")
    )

    settings = BlockchainClientSettings(
        provider_uri=rpc_url,
        chain_id=chain_id,
        contract_address=contract_address,
        signer_private_key=writer_key,
        artifact_path=artifact_path,
        confirmation_blocks=int(os.getenv("MIN_CONFIRMATIONS", "1")),
        proof_of_authority=True,
    )
    client = BlockchainClient(settings)
    client.validate_connection()

    run_id = uuid4().hex
    evidence_ref = to_bytes32(f"besu:evidence:{run_id}")
    static_hash = to_bytes32(f"besu:static:{run_id}")
    officer_ref = to_bytes32(f"besu:officer:{run_id}")
    access_session_ref = to_bytes32(f"besu:session:{run_id}")

    evidence_result = client.record_evidence(evidence_ref, static_hash)
    access_result = client.record_access(evidence_ref, officer_ref, access_session_ref)
    assert client.get_evidence(evidence_ref)["static_hash"] == static_hash
    access = client.get_access_by_session(access_session_ref)
    assert access["evidence_ref"] == evidence_ref
    assert access["officer_ref"] == officer_ref

    verifier = TransactionVerifier(client)
    verifier.verify_evidence_transaction(evidence_result.tx_hash)
    verifier.verify_access_transaction(access_result.tx_hash)

    print(
        json.dumps(
            {
                "record_evidence_tx": evidence_result.tx_hash,
                "record_access_tx": access_result.tx_hash,
                "contract_address": contract_address,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
