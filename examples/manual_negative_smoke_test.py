from __future__ import annotations

import hashlib
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from blockchain_client import BlockchainClient, BlockchainClientSettings
from blockchain_client.exceptions import TransactionSubmissionError

DEFAULT_RPC_URL = "http://127.0.0.1:8545"
DEFAULT_CHAIN_ID = 31337
DEFAULT_FORGE = r"C:\Users\kiadt\.foundry\bin\forge.exe"
DEFAULT_ANVIL_ACCOUNT_0_KEY = (
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
)


def to_bytes32(value: str) -> str:
    """Create a deterministic non-zero bytes32 reference."""

    return "0x" + hashlib.sha256(value.encode("utf-8")).hexdigest()


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

    forge = os.getenv("FORGE_EXE", DEFAULT_FORGE)
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
    unauthorized_key = os.getenv("UNAUTHORIZED_PRIVATE_KEY", DEFAULT_ANVIL_ACCOUNT_0_KEY)
    pauser_key = os.getenv("PAUSER_PRIVATE_KEY", DEFAULT_ANVIL_ACCOUNT_0_KEY)

    writer = make_client(writer_key)
    unauthorized = make_client(unauthorized_key)
    run_id = uuid4().hex

    evidence_ref = to_bytes32(f"negative:evidence:{run_id}")
    static_hash = to_bytes32(f"negative:static:{run_id}")
    duplicate_static_hash = to_bytes32(f"negative:static-duplicate:{run_id}")
    officer_ref = to_bytes32("negative:officer:local-test-001")
    access_session_ref = to_bytes32(f"negative:access-session:{run_id}")

    writer.record_evidence(evidence_ref, static_hash)
    print("[SETUP] recorded initial evidence")

    expect_submission_failure(
        "duplicate evidence_ref",
        lambda: writer.record_evidence(evidence_ref, duplicate_static_hash),
    )

    writer.record_access(evidence_ref, officer_ref, access_session_ref)
    print("[SETUP] recorded initial access session")

    expect_submission_failure(
        "duplicate access_session_ref",
        lambda: writer.record_access(
            evidence_ref,
            to_bytes32("negative:officer:duplicate-attempt"),
            access_session_ref,
        ),
    )

    expect_submission_failure(
        "unauthorized writer",
        lambda: unauthorized.record_evidence(
            to_bytes32(f"negative:unauthorized:evidence:{run_id}"),
            to_bytes32(f"negative:unauthorized:static:{run_id}"),
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
                to_bytes32(f"negative:paused:evidence:{run_id}"),
                to_bytes32(f"negative:paused:static:{run_id}"),
            ),
        )

        expect_submission_failure(
            "paused record_access",
            lambda: writer.record_access(
                evidence_ref,
                to_bytes32("negative:officer:paused-attempt"),
                to_bytes32(f"negative:paused:access-session:{run_id}"),
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
