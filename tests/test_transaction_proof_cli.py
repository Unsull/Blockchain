from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest

from blockchain_client.exceptions import SigningAccountRequiredError, TransactionVerificationError
from tests.proof_fixtures import TX_HASH, evidence_proof


def load_cli() -> ModuleType:
    path = Path("network/besu/scripts/transaction-proof.py")
    spec = importlib.util.spec_from_file_location("transaction_proof_cli", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verification_args(module: ModuleType) -> object:
    return module.build_parser().parse_args(
        [
            "verify-evidence",
            "--tx-hash",
            TX_HASH,
            "--rpc-url",
            "http://127.0.0.1:8545",
            "--chain-id",
            "20260720",
            "--contract-address",
            "0x" + "44" * 20,
            "--artifact-path",
            "tests/fixtures/EvidenceRegistry.json",
        ]
    )


def test_verify_client_does_not_require_writer_private_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = load_cli()
    captured: list[object] = []
    monkeypatch.delenv("WRITER_PRIVATE_KEY", raising=False)
    monkeypatch.setattr(
        module,
        "BlockchainClient",
        lambda settings: captured.append(settings) or object(),
    )

    module.make_client(verification_args(module), signing=False)

    assert captured[0].signer_private_key is None


def test_record_client_requires_writer_private_key(monkeypatch: pytest.MonkeyPatch) -> None:
    module = load_cli()
    monkeypatch.delenv("WRITER_PRIVATE_KEY", raising=False)
    args = module.build_parser().parse_args(
        [
            "record-evidence",
            "--rpc-url",
            "http://127.0.0.1:8545",
            "--chain-id",
            "20260720",
            "--contract-address",
            "0x" + "44" * 20,
        ]
    )

    with pytest.raises(SigningAccountRequiredError):
        module.make_client(args, signing=True)


def test_no_private_key_cli_option_exists() -> None:
    module = load_cli()
    with pytest.raises(SystemExit):
        module.build_parser().parse_args(["record-evidence", "--private-key", "secret"])


def test_verify_command_requires_transaction_hash() -> None:
    module = load_cli()
    with pytest.raises(SystemExit):
        module.build_parser().parse_args(["verify-evidence"])


def test_cli_writes_json_and_markdown_on_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load_cli()
    json_path = tmp_path / "proof.json"
    markdown_path = tmp_path / "proof.md"
    monkeypatch.setattr(module, "execute", lambda args: evidence_proof())

    exit_code = module.main(
        [
            "verify-evidence",
            "--tx-hash",
            TX_HASH,
            "--json-output",
            str(json_path),
            "--markdown-output",
            str(markdown_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text(encoding="utf-8"))["verification_status"] == "verified"
    assert markdown_path.read_text(encoding="utf-8").startswith("# Blockchain")


def test_cli_failure_is_nonzero_and_does_not_finalize_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_cli()
    json_path = tmp_path / "proof.json"
    markdown_path = tmp_path / "proof.md"

    def fail(args: object) -> None:
        raise TransactionVerificationError("transaction not found")

    monkeypatch.setattr(module, "execute", fail)
    exit_code = module.main(
        [
            "verify-evidence",
            "--tx-hash",
            TX_HASH,
            "--json-output",
            str(json_path),
            "--markdown-output",
            str(markdown_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "transaction not found" in captured.err
    assert "Traceback" not in captured.err
    assert not json_path.exists()
    assert not markdown_path.exists()


def test_private_key_sentinel_never_appears_in_cli_or_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = load_cli()
    sentinel = "0x" + "de" * 32
    json_path = tmp_path / "proof.json"
    markdown_path = tmp_path / "proof.md"
    monkeypatch.setenv("WRITER_PRIVATE_KEY", sentinel)
    monkeypatch.setattr(module, "execute", lambda args: evidence_proof())

    assert (
        module.main(
            [
                "verify-evidence",
                "--tx-hash",
                TX_HASH,
                "--json-output",
                str(json_path),
                "--markdown-output",
                str(markdown_path),
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    combined = (
        captured.out
        + captured.err
        + json_path.read_text(encoding="utf-8")
        + markdown_path.read_text(encoding="utf-8")
    )
    assert sentinel not in combined
