#!/usr/bin/env python3
"""Validate the provisioned Besu dashboard through Grafana and Prometheus APIs."""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


def load_env(path: Path) -> dict[str, str]:
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def request_json(
    url: str, auth: tuple[str, str] | None = None, timeout: float = 15.0
) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if auth:
        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        headers["Authorization"] = f"Basic {token}"
    request = urllib.request.Request(url, headers=headers)  # noqa: S310
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        result: dict[str, Any] = json.load(response)
    return result


def prometheus_query(base_url: str, expression: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"query": expression})
    payload = request_json(f"{base_url.rstrip('/')}/api/v1/query?{query}")
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus rejected query: {expression}")
    return payload


def scalar_value(payload: dict[str, Any]) -> float:
    results = payload["data"]["result"]
    if not results:
        raise RuntimeError("required Prometheus query returned no data")
    return float(results[0]["value"][1])


def wait_for_services(prometheus_url: str, grafana_url: str, timeout: float = 90.0) -> None:
    deadline = time.monotonic() + timeout
    last_error = "services not ready"
    while time.monotonic() < deadline:
        try:
            targets = request_json(f"{prometheus_url}/api/v1/targets")
            health = request_json(f"{grafana_url}/api/health")
            active = [
                target
                for target in targets["data"]["activeTargets"]
                if target.get("labels", {}).get("job") == "besu"
            ]
            if len(active) == 5 and all(target["health"] == "up" for target in active):
                if health.get("database") == "ok":
                    return
            last_error = "five UP Besu targets and healthy Grafana database not observed"
        except (OSError, KeyError, TypeError, urllib.error.URLError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(2)
    raise TimeoutError(last_error)


def validate(args: argparse.Namespace) -> dict[str, Any]:
    env = load_env(args.env_file)
    auth = (
        env.get("GRAFANA_ADMIN_USER", "admin"),
        env.get("GRAFANA_ADMIN_PASSWORD", "change-me-local-only"),
    )
    wait_for_services(args.prometheus_url, args.grafana_url)

    target_payload = request_json(f"{args.prometheus_url}/api/v1/targets")
    targets = [
        target
        for target in target_payload["data"]["activeTargets"]
        if target.get("labels", {}).get("job") == "besu"
    ]
    datasource = request_json(
        f"{args.grafana_url}/api/datasources/uid/prometheus/health", auth=auth
    )
    if datasource.get("status") != "OK":
        raise RuntimeError(f"Grafana datasource health is not OK: {datasource.get('status')}")
    dashboard_response = request_json(
        f"{args.grafana_url}/api/dashboards/uid/besu-qbft-overview", auth=auth
    )
    dashboard = dashboard_response["dashboard"]
    if dashboard.get("uid") != "besu-qbft-overview":
        raise RuntimeError("Grafana returned an unexpected dashboard UID")

    query_results = []
    for panel in dashboard["panels"]:
        for target in panel.get("targets", []):
            expression = target["expr"].replace("$instance", ".*")
            result = prometheus_query(args.prometheus_url, expression)
            series_count = len(result["data"]["result"])
            query_results.append(
                {"panel": panel["title"], "ref_id": target["refId"], "series": series_count}
            )

    nodes_online = scalar_value(prometheus_query(args.prometheus_url, 'sum(up{job="besu"})'))
    validators_online = scalar_value(
        prometheus_query(
            args.prometheus_url,
            'sum(up{job="besu",instance=~"validator-[1-4]:9545"})',
        )
    )
    rpc_up = scalar_value(
        prometheus_query(args.prometheus_url, 'up{job="besu",instance="rpc-node:9545"}')
    )
    if (nodes_online, validators_online, rpc_up) != (5.0, 4.0, 1.0):
        raise RuntimeError(
            f"unexpected availability values: nodes={nodes_online}, "
            f"validators={validators_online}, rpc={rpc_up}"
        )

    height_query = 'ethereum_blockchain_height{job="besu",instance="rpc-node:9545"}'
    height_before = scalar_value(prometheus_query(args.prometheus_url, height_query))
    time.sleep(args.block_wait_seconds)
    height_after = scalar_value(prometheus_query(args.prometheus_url, height_query))
    if height_after <= height_before:
        raise RuntimeError(f"block height did not increase: {height_before} -> {height_after}")

    required_data_queries = {
        "memory": 'process_resident_memory_bytes{job="besu"}',
        "peer_count": 'ethereum_peer_count{job="besu"}',
    }
    required_data = {
        name: len(prometheus_query(args.prometheus_url, expression)["data"]["result"])
        for name, expression in required_data_queries.items()
    }
    if any(count == 0 for count in required_data.values()):
        raise RuntimeError(f"required metric returned no data: {required_data}")

    divergence = scalar_value(
        prometheus_query(
            args.prometheus_url,
            'max(ethereum_blockchain_height{job="besu"}) '
            '- min(ethereum_blockchain_height{job="besu"})',
        )
    )
    return {
        "targets": [
            {"instance": target["labels"]["instance"], "health": target["health"]}
            for target in sorted(targets, key=lambda item: item["labels"]["instance"])
        ],
        "grafana_database": "ok",
        "datasource_status": datasource["status"],
        "dashboard_uid": dashboard["uid"],
        "query_count": len(query_results),
        "panels_with_data": [item["panel"] for item in query_results if item["series"] > 0],
        "panels_without_data": [item["panel"] for item in query_results if item["series"] == 0],
        "nodes_online": nodes_online,
        "validators_online": validators_online,
        "rpc_up": rpc_up,
        "height_before": height_before,
        "height_after": height_after,
        "required_data_series": required_data,
        "block_height_divergence": divergence,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:9090")
    parser.add_argument("--grafana-url", default="http://127.0.0.1:3000")
    parser.add_argument("--env-file", type=Path, default=Path("network/besu/.env"))
    parser.add_argument("--block-wait-seconds", type=float, default=20.0)
    return parser.parse_args()


def main() -> int:
    try:
        result = validate(parse_args())
    except (OSError, KeyError, TypeError, ValueError, RuntimeError, TimeoutError) as exc:
        print(f"monitoring validation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
