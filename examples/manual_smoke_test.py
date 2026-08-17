from __future__ import annotations

import os
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

    evidence_id = uuid4()
    evidence_ref = derive_evidence_ref(evidence_id)
    evidence_hash = "0x" + sha256(b"manual-smoke:" + evidence_id.bytes).hexdigest()
    uploader_ref = derive_actor_ref(uuid4())
    officer_ref = derive_actor_ref(uuid4())
    access_session_ref = derive_access_session_ref(uuid4())

    evidence_tx = client.record_evidence(
        evidence_ref=evidence_ref,
        evidence_hash=evidence_hash,
        uploader_ref=uploader_ref,
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
