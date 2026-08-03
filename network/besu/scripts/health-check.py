from __future__ import annotations

import argparse
import json
import time
import urllib.request
from typing import Any


def rpc(rpc_url: str, method: str, params: list[Any] | None = None) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1})
    request = urllib.request.Request(
        rpc_url,
        data=body.encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode())
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload["result"]


def pass_line(label: str) -> None:
    print(f"[PASS] {label}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Besu private network health checks.")
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8545")
    parser.add_argument("--expected-chain-id", type=int, required=True)
    parser.add_argument("--min-peers", type=int, default=3)
    parser.add_argument("--peer-wait-seconds", type=int, default=60)
    parser.add_argument("--block-wait-seconds", type=int, default=15)
    parser.add_argument("--max-block-age-seconds", type=int, default=60)
    args = parser.parse_args()

    client_version = rpc(args.rpc_url, "web3_clientVersion")
    if "besu" not in client_version.lower():
        raise SystemExit(f"unexpected client version: {client_version}")
    pass_line("RPC connected")

    chain_id = int(rpc(args.rpc_url, "eth_chainId"), 16)
    if chain_id != args.expected_chain_id:
        raise SystemExit(f"chain ID mismatch: expected {args.expected_chain_id}, got {chain_id}")
    pass_line("Chain ID")

    start_block = int(rpc(args.rpc_url, "eth_blockNumber"), 16)
    time.sleep(args.block_wait_seconds)
    end_block = int(rpc(args.rpc_url, "eth_blockNumber"), 16)
    if end_block <= start_block:
        raise SystemExit("block number did not increase")
    pass_line("Block production")

    peer_deadline = time.monotonic() + args.peer_wait_seconds
    while True:
        peer_count = int(rpc(args.rpc_url, "net_peerCount"), 16)
        if peer_count >= args.min_peers:
            break
        if time.monotonic() >= peer_deadline:
            raise SystemExit(
                f"peer count too low: expected >= {args.min_peers}, got {peer_count}"
            )
        time.sleep(2)
    pass_line("Peer count")

    syncing = rpc(args.rpc_url, "eth_syncing")
    if syncing is not False:
        raise SystemExit("node is syncing")
    pass_line("Sync status")

    latest = rpc(args.rpc_url, "eth_getBlockByNumber", ["latest", False])
    block_age = int(time.time()) - int(latest["timestamp"], 16)
    if block_age > args.max_block_age_seconds:
        raise SystemExit(f"latest block is too old: {block_age}s")
    pass_line("Latest block timestamp")

    print(json.dumps({"chain_id": chain_id, "block_number": end_block, "peer_count": peer_count}))


if __name__ == "__main__":
    main()
