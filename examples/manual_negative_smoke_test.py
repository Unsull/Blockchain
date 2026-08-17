from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
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
from blockchain_client.exceptions import TransactionSubmissionError

DEFAULT_RPC_URL = "http://127.0.0.1:8545"
DEFAULT_CHAIN_ID = 31337


def sample_evidence_hash(value: bytes) -> str:
    """Hash deterministic local sample evidence bytes."""

    return "0x" + sha256(value).hexdigest()


def make_client(private_key: str) -> BlockchainClient:
    """Create a client from local smoke-test environment variables."""

    settings = BlockchainClientSettings(
        provider_uri=os.getenv("RPC_URL", DEFAULT_RPC_URL),
        chain_id=int(os.getenv("CHAIN_ID", str(DEFAULT_CHAIN_ID))),
        contract_address=os.environ["CONTRACT_ADDRESS"],
        signer_private_key=private_key,
        artifact_path=Path(
            os.getenv("ARTIFACT_PATH", "out/EvidenceRegistry.sol/EvidenceRegistry.json")
        ),
        request_timeout_seconds=30,
        confirmation_blocks=0,
    )
    client = BlockchainClient(settings)
    client.validate_connection()
    return client


def expect_submission_failure(label: str, action: Callable[[], object]) -> None:
    """Run an action that must fail with TransactionSubmissionError."""

    try:
        action()
    except TransactionSubmissionError as exc:
        print(f"[PASS] {label}: rejected ({exc})")
        return
    raise AssertionError(f"[FAIL] {label}: transaction unexpectedly succeeded")


def run_forge_script(script_target: str, extra_env: dict[str, str]) -> None:
    """Run a Foundry script against the configured local RPC."""

    forge = os.getenv("FORGE_EXE") or shutil.which("forge")
    if forge is None:
        raise RuntimeError("forge executable not found; set FORGE_EXE or add forge to PATH")
    env = os.environ.copy()
    env.update(extra_env)
    env.setdefault("RPC_URL", DEFAULT_RPC_URL)
    command = [
        forge,
        "script",
        script_target,
        "--rpc-url",
        env["RPC_URL"],
        "--broadcast",
        "-vvvv",
    ]
    subprocess.run(command, check=True, env=env)


def main() -> None:
    writer_key = os.environ["WRITER_PRIVATE_KEY"]
    unauthorized_key = os.environ["UNAUTHORIZED_PRIVATE_KEY"]
    pauser_key = os.environ["PAUSER_PRIVATE_KEY"]

    writer = make_client(writer_key)
    unauthorized = make_client(unauthorized_key)
    evidence_id = uuid4()
    evidence_ref = derive_evidence_ref(evidence_id)
    evidence_hash = sample_evidence_hash(b"negative:initial:" + evidence_id.bytes)
    duplicate_evidence_hash = sample_evidence_hash(b"negative:duplicate:" + evidence_id.bytes)
    uploader_ref = derive_actor_ref(uuid4())
    officer_ref = derive_actor_ref(uuid4())
    access_session_ref = derive_access_session_ref(uuid4())

    writer.record_evidence(evidence_ref, evidence_hash, uploader_ref)
    print("[SETUP] recorded initial evidence")

    expect_submission_failure(
        "duplicate evidence_ref",
        lambda: writer.record_evidence(
            evidence_ref,
            duplicate_evidence_hash,
            uploader_ref,
        ),
    )

    writer.record_access(evidence_ref, officer_ref, access_session_ref)
    print("[SETUP] recorded initial access session")

    expect_submission_failure(
        "duplicate access_session_ref",
        lambda: writer.record_access(
            evidence_ref,
            derive_actor_ref(uuid4()),
            access_session_ref,
        ),
    )

    expect_submission_failure(
        "unauthorized writer",
        lambda: unauthorized.record_evidence(
            derive_evidence_ref(uuid4()),
            sample_evidence_hash(b"negative:unauthorized"),
            derive_actor_ref(uuid4()),
        ),
    )

    try:
        print("[SETUP] pausing registry")
        run_forge_script(
            "script/PauseRegistry.s.sol:PauseRegistry",
            {"PAUSER_PRIVATE_KEY": pauser_key},
        )

        expect_submission_failure(
            "paused record_evidence",
            lambda: writer.record_evidence(
                derive_evidence_ref(uuid4()),
                sample_evidence_hash(b"negative:paused"),
                derive_actor_ref(uuid4()),
            ),
        )

        expect_submission_failure(
            "paused record_access",
            lambda: writer.record_access(
                evidence_ref,
                derive_actor_ref(uuid4()),
                derive_access_session_ref(uuid4()),
            ),
        )
    finally:
        print("[CLEANUP] unpausing registry")
        run_forge_script(
            "script/UnpauseRegistry.s.sol:UnpauseRegistry",
            {"PAUSER_PRIVATE_KEY": pauser_key},
        )

    print("[PASS] negative smoke tests completed")


if __name__ == "__main__":
    main()
