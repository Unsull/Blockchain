from __future__ import annotations

import json
from pathlib import Path

from blockchain_client.proof_renderer import (
    proof_to_json,
    proof_to_markdown,
    write_json_proof,
    write_markdown_proof,
)
from tests.proof_fixtures import evidence_proof


def test_renderer_produces_valid_json_and_required_markdown() -> None:
    proof = evidence_proof()

    payload = json.loads(proof_to_json(proof))
    markdown = proof_to_markdown(proof)

    assert payload["verification_status"] == "verified"
    assert "# Blockchain Transaction Verification Proof" in markdown
    assert "## Decoded Contract Call" in markdown
    assert "## Verification Checks" in markdown
    assert "## Interpretation" in markdown
    assert "## Reproduction Information" in markdown
    assert "Evidence hash" in markdown
    assert "Uploader reference" in markdown
    assert markdown.count("| PASS |") == 9
    assert "datetime.datetime" not in markdown


def test_writers_create_parent_directories_and_replace_exact_files(tmp_path: Path) -> None:
    proof = evidence_proof()
    json_path = tmp_path / "nested" / "proof.json"
    markdown_path = tmp_path / "nested" / "proof.md"

    write_json_proof(proof, json_path)
    write_markdown_proof(proof, markdown_path)

    assert json.loads(json_path.read_text(encoding="utf-8"))["schema_version"] == "1.0"
    assert markdown_path.read_text(encoding="utf-8").startswith("# Blockchain")
    assert not list(json_path.parent.glob("*.tmp"))


def test_rendered_output_does_not_contain_secret_sentinel() -> None:
    sentinel = "0x" + "de" * 32
    proof = evidence_proof()

    assert sentinel not in proof_to_json(proof)
    assert sentinel not in proof_to_markdown(proof)
