from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a Foundry contract artifact subset.")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=Path("out/EvidenceRegistry.sol/EvidenceRegistry.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    artifact = json.loads(args.artifact.read_text(encoding="utf-8"))
    exported = {
        "contractName": artifact.get("contractName", "EvidenceRegistry"),
        "abi": artifact["abi"],
        "bytecode": artifact.get("bytecode", {}),
        "deployedBytecode": artifact.get("deployedBytecode", {}),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(exported, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
