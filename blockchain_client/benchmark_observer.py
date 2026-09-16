"""Prometheus observation for blockchain benchmark runs."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from csv import DictWriter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path
from typing import Any

from blockchain_client.benchmark_models import BenchmarkExperimentMetadata

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
class PrometheusTimeSeriesSample:
    """One labelled Prometheus range-vector sample."""

    timestamp: datetime
    metric_name: str
    instance: str
    labels: dict[str, str]
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
    experiment: BenchmarkExperimentMetadata | None = None


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
        expected_instances: tuple[str, ...] | None = None,
        allowed_down_instances: tuple[str, ...] = (),
    ) -> None:
        """Validate the exact declared network health condition."""

        up_samples = snapshot.metrics["node_up"]

        by_instance = {
            sample.instance: sample
            for sample in up_samples
        }

        if len(by_instance) != len(up_samples):
            raise RuntimeError(
                "duplicate Besu Prometheus target instance"
            )

        if len(up_samples) != expected_nodes:
            raise RuntimeError(
                "unexpected Besu Prometheus target count: "
                f"expected {expected_nodes}, "
                f"found {len(up_samples)}"
            )

        if expected_instances is not None:
            expected = set(expected_instances)
            actual = set(by_instance)

            if len(expected) != len(expected_instances):
                raise ValueError(
                    "expected Prometheus instances must be unique"
                )

            if actual != expected:
                raise RuntimeError(
                    "unexpected Besu Prometheus targets: "
                    f"missing={sorted(expected - actual)}, "
                    f"extra={sorted(actual - expected)}"
                )
        else:
            expected = set(by_instance)

        allowed_down = set(allowed_down_instances)
        unknown_allowed = allowed_down - expected

        if unknown_allowed:
            raise RuntimeError(
                "allowed-down Prometheus target(s) are unknown: "
                + ", ".join(sorted(unknown_allowed))
            )

        condition_mismatch = [
            instance
            for instance in allowed_down
            if by_instance[instance].value != 0.0
        ]

        if condition_mismatch:
            raise RuntimeError(
                "allowed-down Besu target(s) are still UP: "
                + ", ".join(sorted(condition_mismatch))
            )

        unhealthy = [
            instance
            for instance, sample in by_instance.items()
            if instance not in allowed_down
            and sample.value != 1.0
        ]

        if unhealthy:
            raise RuntimeError(
                "Besu Prometheus target(s) are DOWN: "
                + ", ".join(sorted(unhealthy))
            )

    def capture_range(
        self,
        start: datetime,
        end: datetime,
        *,
        step_seconds: int = 15,
    ) -> tuple[PrometheusTimeSeriesSample, ...]:
        """Capture labelled range samples for the measured run interval."""

        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("Prometheus range timestamps must be timezone-aware")
        if end < start:
            raise ValueError("Prometheus range end cannot precede start")
        if step_seconds <= 0:
            raise ValueError("Prometheus range step must be positive")

        samples: list[PrometheusTimeSeriesSample] = []
        for metric_name, expression in BENCHMARK_PROMETHEUS_QUERIES.items():
            metric_samples = self._query_range(
                metric_name,
                expression,
                start=start,
                end=end,
                step_seconds=step_seconds,
            )
            if not metric_samples:
                raise RuntimeError(
                    "Prometheus range query returned no samples for "
                    f"{metric_name}"
                )
            samples.extend(metric_samples)

        return tuple(
            sorted(
                samples,
                key=lambda sample: (
                    sample.timestamp,
                    sample.metric_name,
                    sample.instance,
                    json.dumps(sample.labels, sort_keys=True),
                ),
            )
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

    def _query_range(
        self,
        metric_name: str,
        expression: str,
        *,
        start: datetime,
        end: datetime,
        step_seconds: int,
    ) -> tuple[PrometheusTimeSeriesSample, ...]:
        params = urllib.parse.urlencode(
            {
                "query": expression,
                "start": start.timestamp(),
                "end": end.timestamp(),
                "step": step_seconds,
            }
        )
        url = f"{self.base_url}/api/v1/query_range?{params}"

        with urllib.request.urlopen(
            url,
            timeout=self.timeout_seconds,
        ) as response:
            payload: dict[str, Any] = json.load(response)

        if payload.get("status") != "success":
            raise RuntimeError(
                "Prometheus range query returned non-success status"
            )

        data = payload.get("data")
        if not isinstance(data, dict) or data.get("resultType") != "matrix":
            raise RuntimeError("invalid Prometheus range response")

        result = data.get("result")
        if not isinstance(result, list):
            raise RuntimeError("invalid Prometheus range result")

        samples: list[PrometheusTimeSeriesSample] = []
        for item in result:
            if not isinstance(item, dict):
                raise RuntimeError("invalid Prometheus range series")
            raw_labels = item.get("metric")
            raw_values = item.get("values")
            if not isinstance(raw_labels, dict) or not isinstance(raw_values, list):
                raise RuntimeError("invalid Prometheus range series")

            labels = {
                str(key): str(value)
                for key, value in raw_labels.items()
            }
            instance = labels.get("instance", "unknown")

            for raw_value in raw_values:
                if not isinstance(raw_value, list | tuple) or len(raw_value) < 2:
                    raise RuntimeError("invalid Prometheus range sample")
                try:
                    timestamp = datetime.fromtimestamp(
                        float(raw_value[0]),
                        tz=UTC,
                    )
                    value = float(raw_value[1])
                except (TypeError, ValueError) as exc:
                    raise RuntimeError(
                        "invalid Prometheus range sample"
                    ) from exc

                samples.append(
                    PrometheusTimeSeriesSample(
                        timestamp=timestamp,
                        metric_name=metric_name,
                        instance=instance,
                        labels=labels,
                        value=value,
                    )
                )

        return tuple(samples)


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
    payload: dict[str, Any] = {
        "run_id": observation.run_id,
        "prometheus_url": observation.prometheus_url,
        "before": _snapshot_payload(
            observation.before
        ),
        "after": _snapshot_payload(
            observation.after
        ),
    }

    if observation.experiment is not None:
        payload["experiment"] = asdict(observation.experiment)

    return payload


def write_prometheus_timeseries(
    run_id: str,
    samples: tuple[PrometheusTimeSeriesSample, ...],
    directory: Path,
) -> Path:
    """Atomically export labelled Prometheus samples for one run."""

    if not run_id.strip():
        raise ValueError("run_id is required")
    if not samples:
        raise ValueError("Prometheus time-series samples are required")

    output = StringIO()
    writer = DictWriter(
        output,
        fieldnames=[
            "timestamp",
            "metric_name",
            "instance",
            "labels",
            "value",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    for sample in samples:
        writer.writerow(
            {
                "timestamp": sample.timestamp.isoformat(),
                "metric_name": sample.metric_name,
                "instance": sample.instance,
                "labels": json.dumps(
                    sample.labels,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "value": sample.value,
            }
        )

    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"metrics-timeseries-{run_id}.csv"
    temporary_path = path.with_name(f".{path.name}.tmp")
    temporary_path.write_text(
        output.getvalue(),
        encoding="utf-8",
        newline="\n",
    )
    temporary_path.replace(path)
    return path


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
