from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


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


def compose(*args: str) -> None:
    subprocess.run(["docker", "compose", "--project-directory", str(ROOT), *args], check=True)


def block_number(rpc_url: str) -> int:
    return int(rpc(rpc_url, "eth_blockNumber"), 16)


def assert_blocks(
    label: str,
    rpc_url: str,
    should_increase: bool,
    wait_seconds: int,
) -> dict[str, object]:
    start = block_number(rpc_url)
    time.sleep(wait_seconds)
    end = block_number(rpc_url)
    passed = end > start if should_increase else end == start
    return {"label": label, "start": start, "end": end, "passed": passed}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Besu failure scenario subset.")
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8545")
    parser.add_argument("--wait-seconds", type=int, default=15)
    parser.add_argument("--output", type=Path, default=ROOT / "logs/failure-test-results.json")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    compose("stop", "validator-4")
    results.append(
        assert_blocks("stop one validator keeps producing", args.rpc_url, True, args.wait_seconds)
    )
    compose("start", "validator-4")
    time.sleep(args.wait_seconds)

    compose("stop", "validator-3", "validator-4")
    results.append(
        assert_blocks("stop two validators halts producing", args.rpc_url, False, args.wait_seconds)
    )
    compose("start", "validator-3", "validator-4")
    time.sleep(args.wait_seconds)
    results.append(
        assert_blocks("restart validators resumes producing", args.rpc_url, True, args.wait_seconds)
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['label']}: {item['start']} -> {item['end']}")
    if not all(item["passed"] for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
