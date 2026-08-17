#!/usr/bin/env python3
"""Record or verify EvidenceRegistry transactions and render structured proofs."""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blockchain_client import (  # noqa: E402
    BlockchainClient,
    BlockchainClientSettings,
    TransactionProofBuilder,
)
from blockchain_client.exceptions import (  # noqa: E402
    BlockchainClientError,
    SigningAccountRequiredError,
)
from blockchain_client.proof_models import TransactionProof  # noqa: E402
from blockchain_client.proof_renderer import (  # noqa: E402
    write_json_proof,
    write_markdown_proof,
)


def synthetic_bytes32(label: str) -> str:
    value = f"phase-2.5b:{label}:{uuid4().hex}"
    return "0x" + hashlib.sha256(value.encode()).hexdigest()


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rpc-url", default=os.getenv("RPC_URL"))
    parser.add_argument("--chain-id", type=int, default=_optional_int("CHAIN_ID"))
    parser.add_argument("--contract-address", default=os.getenv("CONTRACT_ADDRESS"))
    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=Path(os.getenv("ARTIFACT_PATH", "out/EvidenceRegistry.sol/EvidenceRegistry.json")),
    )
    parser.add_argument(
        "--confirmations", type=int, default=_optional_int("MIN_CONFIRMATIONS", default=1)
    )
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    verify_evidence = subparsers.add_parser("verify-evidence")
    add_common_arguments(verify_evidence)
    verify_evidence.add_argument("--tx-hash", required=True)

    verify_access = subparsers.add_parser("verify-access")
    add_common_arguments(verify_access)
    verify_access.add_argument("--tx-hash", required=True)

    record_evidence = subparsers.add_parser("record-evidence")
    add_common_arguments(record_evidence)

    record_access = subparsers.add_parser("record-access")
    add_common_arguments(record_access)
    record_access.add_argument("--evidence-ref", required=True)
    return parser


def _optional_int(name: str, default: int | None = None) -> int | None:
    value = os.getenv(name)
    return int(value) if value is not None else default


def make_client(args: argparse.Namespace, signing: bool) -> BlockchainClient:
    missing = [
        name
        for name, value in (
            ("rpc-url", args.rpc_url),
            ("chain-id", args.chain_id),
            ("contract-address", args.contract_address),
        )
        if value in (None, "")
    ]
    if missing:
        raise ValueError(f"missing required configuration: {', '.join(missing)}")
    private_key = os.getenv("WRITER_PRIVATE_KEY") if signing else None
    if signing and not private_key:
        raise SigningAccountRequiredError("WRITER_PRIVATE_KEY is required for record commands")
    settings = BlockchainClientSettings(
        provider_uri=args.rpc_url,
        chain_id=args.chain_id,
        contract_address=args.contract_address,
        artifact_path=args.artifact_path,
        confirmation_blocks=args.confirmations,
        signer_private_key=private_key,
        proof_of_authority=True,
    )
    return BlockchainClient(settings)


def execute(args: argparse.Namespace) -> TransactionProof:
    signing = args.command.startswith("record-")
    client = make_client(args, signing=signing)
    builder = TransactionProofBuilder(client)
    if args.command == "verify-evidence":
        return builder.build_evidence_proof(args.tx_hash)
    if args.command == "verify-access":
        return builder.build_access_proof(args.tx_hash)
    if args.command == "record-evidence":
        result = client.record_evidence(
            synthetic_bytes32("evidence"),
            synthetic_bytes32("evidence-hash"),
            synthetic_bytes32("uploader"),
        )
        return builder.build_evidence_proof(result.tx_hash)
    if args.command == "record-access":
        result = client.record_access(
            args.evidence_ref,
            synthetic_bytes32("officer"),
            synthetic_bytes32("access-session"),
        )
        return builder.build_access_proof(result.tx_hash)
    raise ValueError(f"unsupported command: {args.command}")


def output_paths(args: argparse.Namespace, proof: TransactionProof) -> tuple[Path, Path]:
    stem = f"{proof.operation}-{proof.transaction.tx_hash[2:]}"
    directory = Path("network/besu/proofs")
    return (
        args.json_output or directory / f"{stem}.json",
        args.markdown_output or directory / f"{stem}.md",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        proof = execute(args)
        json_path, markdown_path = output_paths(args, proof)
        write_json_proof(proof, json_path)
        write_markdown_proof(proof, markdown_path)
    except (BlockchainClientError, OSError, ValueError) as exc:
        print(f"transaction proof failed: {exc}", file=sys.stderr)
        return 1
    print(f"verified {proof.operation} transaction: {proof.transaction.tx_hash}")
    print(f"JSON proof: {json_path}")
    print(f"Markdown proof: {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
