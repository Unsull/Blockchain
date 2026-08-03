from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESTORED_VALIDATORS = ("validator-3", "validator-4")


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


def compose(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        ["docker", "compose", "--project-directory", str(ROOT), *args],
        check=True,
        capture_output=capture,
        text=True,
    )
    return result.stdout


def block_number(rpc_url: str) -> int:
    return int(rpc(rpc_url, "eth_blockNumber"), 16)


def peer_count(rpc_url: str) -> int:
    return int(rpc(rpc_url, "net_peerCount"), 16)


def container_states() -> dict[str, str]:
    raw = compose("ps", "-a", "--format", "json", capture=True)
    payloads: list[dict[str, Any]] = []
    try:
        decoded = json.loads(raw)
        payloads = decoded if isinstance(decoded, list) else [decoded]
    except json.JSONDecodeError:
        payloads = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return {
        str(item.get("Service", item.get("Name", "unknown"))): str(
            item.get("State", item.get("Status", "unknown"))
        )
        for item in payloads
    }


def wait_for_service_running(service: str, timeout: int, poll_interval: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if container_states().get(service) == "running":
            return
        time.sleep(poll_interval)
    raise TimeoutError(f"service did not become running within {timeout}s: {service}")


def peer_observation(rpc_url: str, observed: list[int]) -> None:
    try:
        observed.append(peer_count(rpc_url))
    except Exception:
        pass


def scenario_result(
    scenario: str,
    start_block: int,
    end_block: int,
    started_at: float,
    peers: list[int],
    passed: bool,
) -> dict[str, object]:
    return {
        "scenario": scenario,
        "start_block": start_block,
        "end_block": end_block,
        "elapsed_seconds": round(time.monotonic() - started_at, 3),
        "initial_peer_count": peers[0] if peers else None,
        "minimum_peer_count": min(peers) if peers else None,
        "maximum_peer_count": max(peers) if peers else None,
        "final_peer_count": peers[-1] if peers else None,
        "container_states": container_states(),
        "passed": passed,
    }


def wait_for_block_increase(
    scenario: str,
    rpc_url: str,
    timeout: int,
    poll_interval: float,
) -> dict[str, object]:
    started_at = time.monotonic()
    start = block_number(rpc_url)
    end = start
    peers: list[int] = []
    peer_observation(rpc_url, peers)
    deadline = started_at + timeout
    while end <= start and time.monotonic() < deadline:
        time.sleep(min(poll_interval, max(0, deadline - time.monotonic())))
        end = block_number(rpc_url)
        peer_observation(rpc_url, peers)
    return scenario_result(scenario, start, end, started_at, peers, end > start)


def assert_block_stalled(
    scenario: str,
    rpc_url: str,
    observation_seconds: int,
    poll_interval: float,
) -> dict[str, object]:
    started_at = time.monotonic()
    start = block_number(rpc_url)
    end = start
    peers: list[int] = []
    peer_observation(rpc_url, peers)
    deadline = started_at + observation_seconds
    while end == start and time.monotonic() < deadline:
        time.sleep(min(poll_interval, max(0, deadline - time.monotonic())))
        end = block_number(rpc_url)
        peer_observation(rpc_url, peers)
    return scenario_result(scenario, start, end, started_at, peers, end == start)


def collect_diagnostics(rpc_url: str, output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics: dict[str, object] = {"container_states": container_states()}
    for method, label in (("net_peerCount", "peer_count"), ("eth_blockNumber", "block_number")):
        try:
            diagnostics[label] = int(rpc(rpc_url, method), 16)
        except Exception as exc:
            diagnostics[label] = f"unavailable: {exc}"

    commands = {
        "compose-ps.txt": ("ps", "-a"),
        "validator-logs.txt": (
            "logs",
            "--no-color",
            "validator-1",
            "validator-2",
            "validator-3",
            "validator-4",
        ),
        "rpc-node.log": ("logs", "--no-color", "rpc-node"),
    }
    for filename, command in commands.items():
        try:
            content = compose(*command, capture=True)
        except subprocess.CalledProcessError as exc:
            content = f"command failed with exit code {exc.returncode}\n{exc.stdout}\n{exc.stderr}"
        (output_dir / filename).write_text(content, encoding="utf-8")
    (output_dir / "network-state.json").write_text(
        json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8"
    )
    return diagnostics


def restore_validators(service_timeout: int, poll_interval: float) -> None:
    compose("up", "-d", "--no-deps", *RESTORED_VALIDATORS)
    for service in RESTORED_VALIDATORS:
        wait_for_service_running(service, service_timeout, poll_interval)


def require_passed(result: dict[str, object], timeout: int) -> None:
    if not result["passed"]:
        raise TimeoutError(
            f"{result['scenario']} failed within {timeout}s: "
            f"{result['start_block']} -> {result['end_block']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run readiness-aware Besu failure scenarios.")
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8545")
    parser.add_argument("--progress-timeout-seconds", type=int, default=90)
    parser.add_argument("--recovery-timeout-seconds", type=int, default=180)
    parser.add_argument("--halt-settle-seconds", type=int, default=10)
    parser.add_argument("--halt-observation-seconds", type=int, default=20)
    parser.add_argument("--peer-timeout-seconds", type=int, default=60)
    parser.add_argument("--poll-interval-seconds", type=float, default=2)
    parser.add_argument("--output", type=Path, default=ROOT / "logs/failure-test-results.json")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    diagnostics: dict[str, object] | None = None
    failure: str | None = None
    try:
        compose("stop", "validator-4")
        one_offline = wait_for_block_increase(
            "one validator offline",
            args.rpc_url,
            args.progress_timeout_seconds,
            args.poll_interval_seconds,
        )
        require_passed(one_offline, args.progress_timeout_seconds)

        compose("up", "-d", "--no-deps", "validator-4")
        wait_for_service_running(
            "validator-4", args.peer_timeout_seconds, args.poll_interval_seconds
        )
        restored_one = wait_for_block_increase(
            "validator-4 restored",
            args.rpc_url,
            args.progress_timeout_seconds,
            args.poll_interval_seconds,
        )
        require_passed(restored_one, args.progress_timeout_seconds)
        one_offline["restoration"] = restored_one
        results.append(one_offline)

        compose("stop", "validator-3", "validator-4")
        time.sleep(args.halt_settle_seconds)
        halted = assert_block_stalled(
            "two validators offline",
            args.rpc_url,
            args.halt_observation_seconds,
            args.poll_interval_seconds,
        )
        results.append(halted)
        require_passed(halted, args.halt_observation_seconds)

        restore_validators(args.peer_timeout_seconds, args.poll_interval_seconds)
        recovered = wait_for_block_increase(
            "validator recovery",
            args.rpc_url,
            args.recovery_timeout_seconds,
            args.poll_interval_seconds,
        )
        results.append(recovered)
        require_passed(recovered, args.recovery_timeout_seconds)
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}"
        diagnostics = collect_diagnostics(args.rpc_url, args.output.parent)
    finally:
        try:
            restore_validators(args.peer_timeout_seconds, args.poll_interval_seconds)
        except Exception as exc:
            restoration_error = f"{type(exc).__name__}: {exc}"
            failure = failure or restoration_error
            if diagnostics is None:
                diagnostics = collect_diagnostics(args.rpc_url, args.output.parent)

    payload = {
        "passed": failure is None,
        "scenarios": results,
        "error": failure,
        "diagnostics": diagnostics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        print(f"[{status}] {item['scenario']}: {item['start_block']} -> {item['end_block']}")
    if failure:
        print(f"[FAIL] {failure}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
