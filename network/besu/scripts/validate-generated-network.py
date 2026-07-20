from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated Besu network artifacts.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-validators", type=int, default=4)
    args = parser.parse_args()

    genesis = args.root / "genesis/genesis.json"
    static_nodes = args.root / "build/static-nodes.json"
    if not genesis.exists():
        raise SystemExit("missing generated genesis.json")
    if not static_nodes.exists():
        raise SystemExit("missing static-nodes.json")
    peers = json.loads(static_nodes.read_text(encoding="utf-8"))
    if len(peers) != args.expected_validators:
        raise SystemExit(f"expected {args.expected_validators} static peers, got {len(peers)}")
    for index in range(1, args.expected_validators + 1):
        key = args.root / f"keys/validator-{index}/key"
        public_key = args.root / f"keys/validator-{index}/key.pub"
        if not key.exists() or not public_key.exists():
            raise SystemExit(f"missing key material for validator-{index}")
    print("[PASS] generated network artifacts validated")
