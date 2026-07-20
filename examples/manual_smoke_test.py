from __future__ import annotations

import hashlib
import os
from pathlib import Path
from uuid import uuid4

from blockchain_client import BlockchainClient, BlockchainClientSettings


def to_bytes32(value: str) -> str:
    """Create a deterministic non-zero bytes32 reference."""
    return "0x" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> None:
    contract_address = os.environ["CONTRACT_ADDRESS"]
    writer_private_key = os.environ["WRITER_PRIVATE_KEY"]

    settings = BlockchainClientSettings(
        provider_uri=os.getenv("RPC_URL", "http://127.0.0.1:8545"),
        chain_id=int(os.getenv("CHAIN_ID", "31337")),
        contract_address=contract_address,
        signer_private_key=writer_private_key,
        artifact_path=Path(
            os.getenv("ARTIFACT_PATH", "out/EvidenceRegistry.sol/EvidenceRegistry.json")
        ),
        request_timeout_seconds=30,
        confirmation_blocks=int(os.getenv("MIN_CONFIRMATIONS", "0")),
    )

    client = BlockchainClient(settings)
    client.validate_connection()

    run_id = uuid4().hex

    evidence_ref = to_bytes32(f"evidence:{run_id}")
    static_hash = to_bytes32(f"static-file-content:{run_id}")
    officer_ref = to_bytes32("officer:local-test-001")
    access_session_ref = to_bytes32(f"access-session:{run_id}")

    evidence_tx = client.record_evidence(
        evidence_ref=evidence_ref,
        static_hash=static_hash,
    )
    print("Evidence transaction:")
    print(evidence_tx)

    access_tx = client.record_access(
        evidence_ref=evidence_ref,
        officer_ref=officer_ref,
        access_session_ref=access_session_ref,
    )
    print("\nAccess transaction:")
    print(access_tx)

    evidence = client.get_evidence(evidence_ref)
    print("\nEvidence state:")
    print(evidence)

    access = client.get_access_by_session(access_session_ref)
    print("\nAccess state:")
    print(access)


if __name__ == "__main__":
    main()
