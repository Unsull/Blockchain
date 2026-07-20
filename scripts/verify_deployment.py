from __future__ import annotations

import argparse
import json
from pathlib import Path

from web3 import Web3


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify deployed EvidenceRegistry bytecode.")
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    web3 = Web3(Web3.HTTPProvider(manifest["rpc_url"]))
    if not web3.is_connected():
        raise SystemExit("provider is not connected")
    chain_id = web3.eth.chain_id
    if chain_id != manifest["chain_id"]:
        raise SystemExit(f"chain ID mismatch: expected {manifest['chain_id']}, got {chain_id}")
    address = web3.to_checksum_address(manifest["contract_address"])
    code = web3.eth.get_code(address)
    if code in (b"", "0x", None):
        raise SystemExit("no deployed bytecode at contract address")
    print(f"verified {manifest['contract_name']} at {address} on chain {chain_id}")


if __name__ == "__main__":
    main()
