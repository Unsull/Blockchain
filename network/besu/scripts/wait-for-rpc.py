from __future__ import annotations

import argparse
import json
import time
import urllib.request


def rpc_call(rpc_url: str) -> bool:
    body = json.dumps({"jsonrpc": "2.0", "method": "web3_clientVersion", "params": [], "id": 1})
    request = urllib.request.Request(
        rpc_url,
        data=body.encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        payload = json.loads(response.read().decode())
    return "result" in payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for Besu RPC to answer JSON-RPC.")
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8545")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()

    deadline = time.monotonic() + args.timeout_seconds
    while time.monotonic() < deadline:
        try:
            if rpc_call(args.rpc_url):
                print("[PASS] RPC connected")
                return
        except Exception:
            time.sleep(2)
    raise SystemExit("RPC did not become ready")


if __name__ == "__main__":
    main()
