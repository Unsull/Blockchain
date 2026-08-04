#!/usr/bin/env python3
"""Discover live Besu metrics through the read-only Prometheus HTTP API."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

KEYWORDS = (
    "block",
    "blockchain",
    "height",
    "peer",
    "transaction",
    "tx",
    "pool",
    "qbft",
    "consensus",
    "process",
    "memory",
    "jvm",
    "cpu",
    "thread",
    "file",
    "rpc",
    "sync",
)

CATEGORIES: dict[str, dict[str, Any]] = {
    "node availability": {"metrics": ["up"], "status": "confirmed available"},
    "block height": {
        "metrics": ["ethereum_blockchain_height"],
        "status": "confirmed available",
    },
    "block production rate": {
        "metrics": ["ethereum_blockchain_height"],
        "status": "requires derived PromQL",
        "promql": "rate(ethereum_blockchain_height[5m])",
    },
    "block interval": {
        "metrics": ["ethereum_blockchain_height"],
        "status": "requires derived PromQL",
        "promql": "1 / rate(ethereum_blockchain_height[5m])",
    },
    "peer count": {"metrics": ["ethereum_peer_count"], "status": "confirmed available"},
    "transaction pool": {
        "metrics": ["besu_transaction_pool_number_of_transactions"],
        "status": "confirmed available",
    },
    "transaction count": {
        "metrics": ["besu_blockchain_chain_head_transaction_count"],
        "status": "confirmed available",
    },
    "JVM memory": {"metrics": ["jvm_memory_used_bytes"], "status": "confirmed available"},
    "process memory": {
        "metrics": ["process_resident_memory_bytes"],
        "status": "confirmed available",
    },
    "CPU": {
        "metrics": ["process_cpu_seconds_total"],
        "status": "requires derived PromQL",
        "promql": "rate(process_cpu_seconds_total[5m])",
    },
    "thread count": {"metrics": ["jvm_threads_current"], "status": "confirmed available"},
    "garbage collection": {
        "metrics": ["jvm_gc_collection_seconds_count", "jvm_gc_collection_seconds_sum"],
        "status": "confirmed available",
    },
    "open file descriptors": {
        "metrics": ["process_open_fds"],
        "status": "confirmed available",
    },
    "QBFT or consensus metrics": {
        "metrics": ["besu_executors_bfttimerexecutor_qbft_active_threads_current"],
        "status": "partially available",
    },
    "RPC metrics": {
        "metrics": ["besu_rpc_active_http_connection_count"],
        "status": "confirmed available",
    },
    "sync status": {"metrics": ["besu_synchronizer_in_sync"], "status": "confirmed available"},
}


def filter_metric_names(names: list[str], keywords: tuple[str, ...] = KEYWORDS) -> list[str]:
    """Return sorted metric names containing at least one keyword."""
    lowered = tuple(keyword.lower() for keyword in keywords)
    return sorted({name for name in names if any(word in name.lower() for word in lowered)})


def summarize_vector(result: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    """Reduce a Prometheus instant-vector response to bounded, serializable samples."""
    series = result.get("data", {}).get("result", [])[:limit]
    samples = []
    for item in series:
        labels = dict(sorted(item.get("metric", {}).items()))
        value = item.get("value", [None, None])
        samples.append({"labels": labels, "timestamp": value[0], "value": value[1]})
    return {
        "result_type": result.get("data", {}).get("resultType", "unknown"),
        "samples": samples,
        "instances": sorted(
            {sample["labels"]["instance"] for sample in samples if "instance" in sample["labels"]}
        ),
    }


class PrometheusClient:
    def __init__(self, base_url: str, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def get(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        query = urllib.parse.urlencode(params or {})
        url = f"{self.base_url}{path}" + (f"?{query}" if query else "")
        with urllib.request.urlopen(url, timeout=self.timeout) as response:  # noqa: S310
            payload: dict[str, Any] = json.load(response)
        if payload.get("status") != "success":
            raise RuntimeError(f"Prometheus API returned non-success status for {path}")
        return payload


def likely_use(name: str) -> str:
    uses = []
    for category, spec in CATEGORIES.items():
        if name in spec["metrics"]:
            uses.append(category)
    return ", ".join(uses) if uses else "Supporting node diagnostics"


def limitations(name: str) -> str:
    if "peer" in name:
        return "Direct P2P connections; this is not a QBFT quorum measurement."
    if "qbft" in name:
        return "Executor activity only; it does not expose validator votes or quorum."
    if name == "ethereum_blockchain_height":
        return "Chain height is not transaction, evidence, or access-record count."
    if "transaction_count" in name:
        return "Describes chain-head transactions, not application evidence records."
    return "Metric semantics are limited to the Besu process and labels shown."


def classify_categories(available: set[str]) -> list[dict[str, Any]]:
    classifications = []
    for category, configured in CATEGORIES.items():
        found = [name for name in configured["metrics"] if name in available]
        status = configured["status"]
        if not found:
            status = "unavailable"
        classifications.append(
            {
                "category": category,
                "status": status,
                "metrics": found,
                "expected_metrics": configured["metrics"],
                "promql": configured.get("promql"),
            }
        )
    return classifications


def markdown_report(document: dict[str, Any]) -> str:
    environment = document["environment"]
    lines = [
        "# Besu 26.7.0 Discovered Prometheus Metrics",
        "",
        "## Environment",
        "",
        f"- Besu version: {environment['besu_version']}",
        f"- Node count: {environment['node_count']}",
        f"- Validator count: {environment['validator_count']}",
        f"- RPC node count: {environment['rpc_node_count']}",
        f"- Prometheus scrape interval: {environment['scrape_interval']}",
        f"- Discovery timestamp (UTC): {environment['discovery_timestamp_utc']}",
        "",
        "## Target Status",
        "",
        "| Instance | Health | Last scrape | Scrape duration (s) | Last error |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for target in document["targets"]:
        error = str(target["last_error"]).replace("|", "\\|") or "-"
        lines.append(
            f"| {target['instance']} | {target['health']} | {target['last_scrape']} | "
            f"{target['last_scrape_duration']} | {error} |"
        )
    lines.extend(["", "## Discovered Metrics", ""])
    for metric in document["metrics"]:
        sample = metric["samples"][0] if metric["samples"] else {"labels": {}, "value": "no sample"}
        labels = ", ".join(sample["labels"].keys()) or "none"
        instances = ", ".join(metric["instances"]) or "none in bounded sample"
        lines.extend(
            [
                f"### `{metric['name']}`",
                "",
                f"- Result type: {metric['result_type']}",
                f"- Labels: {labels}",
                f"- Sample value: `{sample['value']}`",
                f"- Instances (up to 5 sampled series): {instances}",
                f"- Likely dashboard use: {metric['likely_dashboard_use']}",
                f"- Limitations: {metric['limitations']}",
                "",
            ]
        )
    lines.extend(["## Metrics Required for Dashboard", ""])
    for item in document["classifications"]:
        found = ", ".join(f"`{name}`" for name in item["metrics"]) or "none"
        detail = f"; PromQL: `{item['promql']}`" if item["promql"] else ""
        lines.append(f"- **{item['category']}**: {item['status']}; metrics: {found}{detail}")
    lines.extend(
        [
            "",
            "QBFT health must be inferred from block progress, validator target availability, "
            "and peer "
            "connectivity. These indicators are not a direct quorum metric.",
            "",
        ]
    )
    return "\n".join(lines)


def discover(client: PrometheusClient, expected_targets: int) -> dict[str, Any]:
    target_payload = client.get("/api/v1/targets")
    active_targets = target_payload["data"]["activeTargets"]
    besu_targets = [
        target
        for target in active_targets
        if target.get("labels", {}).get("job") == "besu"
    ]
    if len(besu_targets) != expected_targets:
        raise RuntimeError(f"expected {expected_targets} Besu targets, found {len(besu_targets)}")
    unhealthy = [
        target["labels"].get("instance", "unknown")
        for target in besu_targets
        if target["health"] != "up"
    ]
    if unhealthy:
        raise RuntimeError(f"Besu targets are not UP: {', '.join(unhealthy)}")

    names_payload = client.get("/api/v1/label/__name__/values")
    all_names = set(names_payload["data"])
    candidate_names = filter_metric_names(list(all_names))
    metrics = []
    for name in candidate_names:
        summary = summarize_vector(client.get("/api/v1/query", {"query": f'{name}{{job="besu"}}'}))
        metrics.append(
            {
                "name": name,
                **summary,
                "likely_dashboard_use": likely_use(name),
                "limitations": limitations(name),
            }
        )

    targets = []
    for target in sorted(besu_targets, key=lambda item: item["labels"]["instance"]):
        targets.append(
            {
                "job": target["labels"].get("job", ""),
                "instance": target["labels"].get("instance", ""),
                "health": target.get("health", "unknown"),
                "last_scrape": target.get("lastScrape", ""),
                "last_scrape_duration": target.get("lastScrapeDuration", 0),
                "last_error": target.get("lastError", ""),
            }
        )
    return {
        "environment": {
            "besu_version": "26.7.0",
            "node_count": 5,
            "validator_count": 4,
            "rpc_node_count": 1,
            "scrape_interval": "15s",
            "discovery_timestamp_utc": datetime.now(UTC).isoformat(),
        },
        "targets": targets,
        "candidate_metric_count": len(metrics),
        "metrics": metrics,
        "classifications": classify_categories(all_names),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prometheus-url", default="http://127.0.0.1:9090")
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--expected-targets", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        document = discover(PrometheusClient(args.prometheus_url), args.expected_targets)
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
        args.markdown_output.write_text(markdown_report(document), encoding="utf-8")
    except (OSError, KeyError, TypeError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        print(f"metric discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"Discovered {document['candidate_metric_count']} candidate metrics from 5 UP targets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
