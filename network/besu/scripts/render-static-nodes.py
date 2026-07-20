from __future__ import annotations

import argparse
import json
from pathlib import Path

SERVICES = ["validator-1", "validator-2", "validator-3", "validator-4"]


def read_public_key(path: Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    if key.startswith("0x"):
        key = key[2:]
    if len(key) != 128:
        raise SystemExit(f"invalid public key length for {path}")
    return key


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render Besu static-nodes.json from generated keys."
    )
    parser.add_argument("--keys-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    enodes = []
    for service in SERVICES:
        public_key = read_public_key(args.keys_dir / service / "key.pub")
        enodes.append(f"enode://{public_key}@{service}:30303")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(enodes, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] static peer count: {len(enodes)}")


if __name__ == "__main__":
    main()
