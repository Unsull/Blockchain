"""Prometheus observation for blockchain benchmark runs."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BENCHMARK_PROMETHEUS_QUERIES: dict[str, str] = {
    "node_up": 'up{job="besu"}',
    "block_height": 'ethereum_blockchain_height{job="besu"}',
    "peer_count": 'ethereum_peer_count{job="besu"}',
    "transaction_pool": (
        'besu_transaction_pool_number_of_transactions{job="besu"}'
    ),
    "chain_head_transaction_count": (
        'besu_blockchain_chain_head_transaction_count{job="besu"}'
    ),
    "jvm_memory_used_bytes": (
        'jvm_memory_used_bytes{job="besu"}'
    ),
    "process_resident_memory_bytes": (
        'process_resident_memory_bytes{job="besu"}'
    ),
    "process_cpu_rate": (
        'rate(process_cpu_seconds_total{job="besu"}[5m])'
    ),
    "rpc_active_connections": (
        'besu_rpc_active_http_connection_count{job="besu"}'
    ),
    "sync_status": (
        'besu_synchronizer_in_sync{job="besu"}'
    ),
}


@dataclass(frozen=True)
class PrometheusSample:
    """One Prometheus instant-vector sample."""

    instance: str
    value: float


@dataclass(frozen=True)
class BenchmarkNetworkSnapshot:
    """Network state captured at one benchmark boundary."""

    captured_at: datetime
    metrics: dict[str, tuple[PrometheusSample, ...]]


@dataclass(frozen=True)
class BenchmarkNetworkObservation:
    """Prometheus state before and after one benchmark run."""

    run_id: str
    prometheus_url: str
    before: BenchmarkNetworkSnapshot
    after: BenchmarkNetworkSnapshot


class PrometheusObserver:
    """Read benchmark-related metrics from Prometheus."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: float = 10.0,
    ) -> None:
        if not base_url.strip():
            raise ValueError("Prometheus base URL is required")

        if timeout_seconds <= 0:
            raise ValueError(
                "Prometheus timeout must be positive"
            )

        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def capture(self) -> BenchmarkNetworkSnapshot:
        """Capture all configured benchmark metrics."""

        metrics = {
            name: self._query(expression)
            for name, expression
            in BENCHMARK_PROMETHEUS_QUERIES.items()
        }

        return BenchmarkNetworkSnapshot(
            captured_at=datetime.now(UTC),
            metrics=metrics,
        )

    def validate_snapshot(
        self,
        snapshot: BenchmarkNetworkSnapshot,
        *,
        expected_nodes: int = 5,
    ) -> None:
        """Validate minimum network health requirements."""

        up_samples = snapshot.metrics["node_up"]

        if len(up_samples) != expected_nodes:
            raise RuntimeError(
                "unexpected Besu Prometheus target count: "
                f"expected {expected_nodes}, "
                f"found {len(up_samples)}"
            )

        unhealthy = [
            sample.instance
            for sample in up_samples
            if sample.value != 1.0
        ]

        if unhealthy:
            raise RuntimeError(
                "Besu Prometheus target(s) are DOWN: "
                + ", ".join(sorted(unhealthy))
            )

    def _query(
        self,
        expression: str,
    ) -> tuple[PrometheusSample, ...]:
        params = urllib.parse.urlencode(
            {"query": expression}
        )

        url = (
            f"{self.base_url}/api/v1/query?"
            f"{params}"
        )

        with urllib.request.urlopen(
            url,
            timeout=self.timeout_seconds,
        ) as response:
            payload: dict[str, Any] = json.load(
                response
            )

        if payload.get("status") != "success":
            raise RuntimeError(
                "Prometheus query returned non-success status"
            )

        result = payload.get("data", {}).get(
            "result",
            [],
        )

        samples: list[PrometheusSample] = []

        for item in result:
            metric = item.get("metric", {})
            raw_value = item.get(
                "value",
                [None, None],
            )

            if len(raw_value) < 2:
                raise RuntimeError(
                    "invalid Prometheus vector sample"
                )

            samples.append(
                PrometheusSample(
                    instance=str(
                        metric.get(
                            "instance",
                            "unknown",
                        )
                    ),
                    value=float(raw_value[1]),
                )
            )

        return tuple(
            sorted(
                samples,
                key=lambda sample: sample.instance,
            )
        )


def write_network_observation(
    observation: BenchmarkNetworkObservation,
    directory: Path,
) -> Path:
    """Atomically export one benchmark network observation."""

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = directory / (
        f"network-{observation.run_id}.json"
    )

    temporary_path = path.with_name(
        f".{path.name}.tmp"
    )

    payload = _observation_payload(
        observation
    )

    temporary_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    temporary_path.replace(path)

    return path


def _observation_payload(
    observation: BenchmarkNetworkObservation,
) -> dict[str, Any]:
    return {
        "run_id": observation.run_id,
        "prometheus_url": observation.prometheus_url,
        "before": _snapshot_payload(
            observation.before
        ),
        "after": _snapshot_payload(
            observation.after
        ),
    }


def _snapshot_payload(
    snapshot: BenchmarkNetworkSnapshot,
) -> dict[str, Any]:
    return {
        "captured_at": snapshot.captured_at.isoformat(),
        "metrics": {
            name: [
                asdict(sample)
                for sample in samples
            ]
            for name, samples
            in snapshot.metrics.items()
        },
    }