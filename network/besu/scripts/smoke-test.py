from __future__ import annotations

import json
import os
import subprocess
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from blockchain_client import (
    BlockchainClient,
    BlockchainClientSettings,
    derive_access_session_ref,
    derive_actor_ref,
    derive_evidence_ref,
)
from blockchain_client.transaction_verifier import TransactionVerifier

ROOT = Path(__file__).resolve().parents[3]


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

    evidence_id = uuid4()
    uploader_id = uuid4()
    officer_id = uuid4()
    access_log_id = uuid4()
    # Blockchain integration:
    # Runtime smoke uses the same canonical references that the Capstone backend
    # will use after repository integration.
    evidence_ref = derive_evidence_ref(evidence_id)
    evidence_hash = "0x" + sha256(b"besu-v2-smoke:" + evidence_id.bytes).hexdigest()
    uploader_ref = derive_actor_ref(uploader_id)
    officer_ref = derive_actor_ref(officer_id)
    access_session_ref = derive_access_session_ref(access_log_id)

    evidence_result = client.record_evidence(evidence_ref, evidence_hash, uploader_ref)
    evidence = client.get_evidence(evidence_ref)
    assert evidence["evidence_hash"] == evidence_hash
    assert evidence["uploader_ref"] == uploader_ref
    evidence_event = client.get_evidence_record_event(
        evidence_ref,
        from_block=evidence_result.block_number,
    )
    assert evidence_event is not None
    assert evidence_event.evidence_hash == evidence_hash
    assert evidence_event.uploader_ref == uploader_ref
    assert evidence_event.tx_hash == evidence_result.tx_hash

    access_result = client.record_access(evidence_ref, officer_ref, access_session_ref)
    access = client.get_access_by_session(access_session_ref)
    assert access["evidence_ref"] == evidence_ref
    assert access["officer_ref"] == officer_ref
    access_events = client.list_access_events(
        evidence_ref,
        from_block=access_result.block_number,
    )
    assert any(event.access_session_ref == access_session_ref for event in access_events)
    access_event = client.get_access_event_by_session(
        access_session_ref,
        from_block=access_result.block_number,
    )
    assert access_event is not None
    assert access_event.evidence_ref == evidence_ref
    assert access_event.officer_ref == officer_ref
    assert access_event.tx_hash == access_result.tx_hash

    verifier = TransactionVerifier(client)
    evidence_proof = verifier.verify_evidence_transaction(evidence_result.tx_hash)
    access_proof = verifier.verify_access_transaction(access_result.tx_hash)
    assert evidence_proof.status == "verified"
    assert access_proof.status == "verified"

    print(
        json.dumps(
            {
                "record_evidence_tx": evidence_result.tx_hash,
                "record_access_tx": access_result.tx_hash,
                "record_evidence_block": evidence_result.block_number,
                "record_access_block": access_result.block_number,
                "contract_address": contract_address,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
