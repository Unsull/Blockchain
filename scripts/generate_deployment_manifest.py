from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an EvidenceRegistry deployment manifest."
    )
    parser.add_argument("--network", required=True)
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--chain-id", type=int, required=True)
    parser.add_argument("--contract-address", required=True)
    parser.add_argument("--deployer-address", required=True)
    parser.add_argument("--admin-address", required=True)
    parser.add_argument("--contract-name", default="EvidenceRegistryV3")
    parser.add_argument("--contract-version", default="V3")
    parser.add_argument(
        "--artifact",
        default="out/EvidenceRegistryV3.sol/EvidenceRegistryV3.json",
    )
    parser.add_argument(
        "--abi-fixture",
        default="tests/fixtures/EvidenceRegistryV3.json",
    )
    parser.add_argument("--deployment-transaction")
    parser.add_argument("--deployment-block", type=int)
    parser.add_argument("--writer-address")
    parser.add_argument("--writer-role-grant-transaction")
    parser.add_argument("--writer-role-grant-block", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "network": args.network,
        "rpc_url": args.rpc_url,
        "chain_id": args.chain_id,
        "contract_name": args.contract_name,
        "contract_version": args.contract_version,
        "contract_address": args.contract_address,
        "deployment_transaction": args.deployment_transaction,
        "deployment_block": args.deployment_block,
        "deployer_address": args.deployer_address,
        "admin_address": args.admin_address,
        "writer_address": args.writer_address,
        "writer_role_grant_transaction": args.writer_role_grant_transaction,
        "writer_role_grant_block": args.writer_role_grant_block,
        "artifact_path": args.artifact,
        "abi_fixture_path": args.abi_fixture,
        "git_commit": git_output("rev-parse", "HEAD"),
        "git_branch": git_output("branch", "--show-current"),
        "foundry": {
            "forge_version": subprocess.check_output(["forge", "--version"], text=True).strip(),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
