from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ADDRESS_PATTERN = re.compile(r"(?:0x)?([0-9a-fA-F]{40})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fund public accounts in a local Besu genesis.")
    parser.add_argument("--genesis", type=Path, required=True)
    parser.add_argument("--address", action="append", required=True)
    parser.add_argument("--balance-wei", type=int, default=10**24)
    args = parser.parse_args()
    if args.balance_wei <= 0:
        raise SystemExit("balance must be positive")

    payload = json.loads(args.genesis.read_text(encoding="utf-8"))
    alloc = payload.setdefault("alloc", {})
    addresses: set[str] = set()
    for raw_address in args.address:
        match = ADDRESS_PATTERN.fullmatch(raw_address)
        if not match:
            raise SystemExit(f"invalid account address: {raw_address}")
        addresses.add(match.group(1).lower())
    for address in addresses:
        alloc[address] = {"balance": hex(args.balance_wei)}
    args.genesis.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] funded {len(addresses)} public account(s) in genesis")


if __name__ == "__main__":
    main()
