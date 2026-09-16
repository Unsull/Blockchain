"""Tests for Prometheus benchmark network observation."""

import csv
import json
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from blockchain_client.benchmark_observer import (
    BenchmarkNetworkObservation,
    BenchmarkNetworkSnapshot,
    PrometheusObserver,
    PrometheusSample,
    PrometheusTimeSeriesSample,
    write_network_observation,
    write_prometheus_timeseries,
)

EXPECTED_INSTANCES = (
    "validator-1:9545",
    "validator-2:9545",
    "validator-3:9545",
    "validator-4:9545",
    "rpc-node:9545",
)


def make_snapshot(
    *,
    node_values: tuple[float, ...] = (1.0, 1.0, 1.0, 1.0, 1.0),
) -> BenchmarkNetworkSnapshot:
    """Create a synthetic network snapshot for validation tests."""

    node_samples = tuple(
        PrometheusSample(
            instance=EXPECTED_INSTANCES[index - 1],
            value=value,
        )
        for index, value in enumerate(
            node_values,
            start=1,
        )
    )

    return BenchmarkNetworkSnapshot(
        captured_at=datetime(
            2026,
            8,
            14,
            12,
            0,
            tzinfo=UTC,
        ),
        metrics={
            "node_up": node_samples,
            "block_height": (
                PrometheusSample(
                    instance="rpc-node:9545",
                    value=500.0,
                ),
            ),
        },
    )


def prometheus_response(
    result: list[dict[str, Any]],
) -> BytesIO:
    """Return a file-like synthetic Prometheus HTTP response."""

    payload = {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": result,
        },
    }

    return BytesIO(
        json.dumps(payload).encode("utf-8")
    )


def test_query_parses_and_sorts_prometheus_samples(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_url: list[str] = []
    captured_timeout: list[float] = []

    def fake_urlopen(
        url: str,
        *,
        timeout: float,
    ) -> BytesIO:
        captured_url.append(url)
        captured_timeout.append(timeout)

        return prometheus_response(
            [
                {
                    "metric": {
                        "instance": "validator-2:9545",
                    },
                    "value": [
                        1_786_000_000,
                        "20",
                    ],
                },
                {
                    "metric": {
                        "instance": "validator-1:9545",
                    },
                    "value": [
                        1_786_000_000,
                        "10",
                    ],
                },
            ]
        )

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    observer = PrometheusObserver(
        "http://127.0.0.1:9090",
        timeout_seconds=5,
    )

    samples = observer._query(
        'ethereum_peer_count{job="besu"}'
    )

    assert [
        sample.instance
        for sample in samples
    ] == [
        "validator-1:9545",
        "validator-2:9545",
    ]

    assert [
        sample.value
        for sample in samples
    ] == [
        10.0,
        20.0,
    ]

    assert captured_timeout == [5]

    assert len(captured_url) == 1
    assert "/api/v1/query?" in captured_url[0]
    assert "ethereum_peer_count" in captured_url[0]


def test_query_rejects_non_success_prometheus_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_urlopen(
        url: str,
        *,
        timeout: float,
    ) -> BytesIO:
        del url
        del timeout

        payload = {
            "status": "error",
            "error": "synthetic failure",
        }

        return BytesIO(
            json.dumps(payload).encode("utf-8")
        )

    monkeypatch.setattr(
        "urllib.request.urlopen",
        fake_urlopen,
    )

    observer = PrometheusObserver(
        "http://127.0.0.1:9090"
    )

    with pytest.raises(
        RuntimeError,
        match="non-success status",
    ):
        observer._query('up{job="besu"}')


def test_validate_snapshot_accepts_five_up_nodes() -> None:
    observer = PrometheusObserver(
        "http://127.0.0.1:9090"
    )

    snapshot = make_snapshot()

    observer.validate_snapshot(
        snapshot,
        expected_nodes=5,
        expected_instances=EXPECTED_INSTANCES,
    )


def test_validate_snapshot_accepts_declared_three_of_four_condition() -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")
    snapshot = make_snapshot(node_values=(1.0, 1.0, 1.0, 0.0, 1.0))

    observer.validate_snapshot(
        snapshot,
        expected_instances=EXPECTED_INSTANCES,
        allowed_down_instances=("validator-4:9545",),
    )


def test_validate_snapshot_rejects_allowed_down_instance_that_is_up() -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")

    with pytest.raises(RuntimeError, match="still UP"):
        observer.validate_snapshot(
            make_snapshot(),
            expected_instances=EXPECTED_INSTANCES,
            allowed_down_instances=("validator-4:9545",),
        )


def test_validate_snapshot_rejects_unexpected_validator_down() -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")

    with pytest.raises(RuntimeError, match="validator-3:9545"):
        observer.validate_snapshot(
            make_snapshot(node_values=(1.0, 1.0, 0.0, 0.0, 1.0)),
            expected_instances=EXPECTED_INSTANCES,
            allowed_down_instances=("validator-4:9545",),
        )


def test_validate_snapshot_rejects_rpc_down_in_degraded_condition() -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")

    with pytest.raises(RuntimeError, match="rpc-node:9545"):
        observer.validate_snapshot(
            make_snapshot(node_values=(1.0, 1.0, 1.0, 0.0, 0.0)),
            expected_instances=EXPECTED_INSTANCES,
            allowed_down_instances=("validator-4:9545",),
        )


def test_validate_snapshot_rejects_down_node() -> None:
    observer = PrometheusObserver(
        "http://127.0.0.1:9090"
    )

    snapshot = make_snapshot(
        node_values=(
            1.0,
            1.0,
            0.0,
            1.0,
            1.0,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="DOWN",
    ):
        observer.validate_snapshot(
            snapshot,
            expected_nodes=5,
        )


def test_validate_snapshot_rejects_wrong_node_count() -> None:
    observer = PrometheusObserver(
        "http://127.0.0.1:9090"
    )

    snapshot = make_snapshot(
        node_values=(
            1.0,
            1.0,
            1.0,
            1.0,
        )
    )

    with pytest.raises(
        RuntimeError,
        match="unexpected Besu Prometheus target count",
    ):
        observer.validate_snapshot(
            snapshot,
            expected_nodes=5,
        )


def test_validate_snapshot_rejects_unknown_or_missing_targets() -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")
    snapshot = make_snapshot()
    samples = list(snapshot.metrics["node_up"])
    samples[-1] = PrometheusSample("unexpected:9545", 1.0)
    changed = BenchmarkNetworkSnapshot(
        captured_at=snapshot.captured_at,
        metrics={**snapshot.metrics, "node_up": tuple(samples)},
    )

    with pytest.raises(RuntimeError, match="unexpected Besu Prometheus targets"):
        observer.validate_snapshot(
            changed,
            expected_instances=EXPECTED_INSTANCES,
        )


def test_observer_rejects_empty_base_url() -> None:
    with pytest.raises(
        ValueError,
        match="base URL is required",
    ):
        PrometheusObserver("")


def test_observer_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="timeout must be positive",
    ):
        PrometheusObserver(
            "http://127.0.0.1:9090",
            timeout_seconds=0,
        )


def test_write_network_observation_creates_expected_json(
    tmp_path: Path,
) -> None:
    before = make_snapshot()

    after = BenchmarkNetworkSnapshot(
        captured_at=datetime(
            2026,
            8,
            14,
            12,
            1,
            tzinfo=UTC,
        ),
        metrics={
            "node_up": tuple(
                PrometheusSample(
                    instance=f"node-{index}:9545",
                    value=1.0,
                )
                for index in range(1, 6)
            ),
            "block_height": (
                PrometheusSample(
                    instance="rpc-node:9545",
                    value=520.0,
                ),
            ),
        },
    )

    observation = BenchmarkNetworkObservation(
        run_id="run-001",
        prometheus_url="http://127.0.0.1:9090",
        before=before,
        after=after,
    )

    output_path = write_network_observation(
        observation,
        tmp_path,
    )

    assert output_path == (
        tmp_path / "network-run-001.json"
    )

    assert output_path.exists()

    payload = json.loads(
        output_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["run_id"] == "run-001"

    assert (
        payload["prometheus_url"]
        == "http://127.0.0.1:9090"
    )

    assert (
        payload["before"]["metrics"]
        ["block_height"][0]["value"]
        == 500.0
    )

    assert (
        payload["after"]["metrics"]
        ["block_height"][0]["value"]
        == 520.0
    )

    assert (
        len(
            payload["before"]["metrics"]
            ["node_up"]
        )
        == 5
    )


def test_write_network_observation_replaces_existing_file(
    tmp_path: Path,
) -> None:
    output_path = (
        tmp_path / "network-run-001.json"
    )

    output_path.write_text(
        "old-content",
        encoding="utf-8",
    )

    snapshot = make_snapshot()

    observation = BenchmarkNetworkObservation(
        run_id="run-001",
        prometheus_url="http://127.0.0.1:9090",
        before=snapshot,
        after=snapshot,
    )

    written_path = write_network_observation(
        observation,
        tmp_path,
    )

    assert written_path == output_path

    payload = json.loads(
        written_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["run_id"] == "run-001"

    temporary_path = (
        tmp_path / ".network-run-001.json.tmp"
    )

    assert not temporary_path.exists()


def test_query_range_preserves_labels_and_uses_requested_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_url: list[str] = []

    def fake_urlopen(url: str, *, timeout: float) -> BytesIO:
        del timeout
        captured_url.append(url)
        payload = {
            "status": "success",
            "data": {
                "resultType": "matrix",
                "result": [
                    {
                        "metric": {
                            "instance": "validator-1:9545",
                            "area": "heap",
                        },
                        "values": [
                            [1_786_000_000, "100"],
                            [1_786_000_015, "110"],
                        ],
                    }
                ],
            },
        }
        return BytesIO(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    observer = PrometheusObserver("http://127.0.0.1:9090")
    start = datetime.fromtimestamp(1_786_000_000, tz=UTC)

    samples = observer._query_range(
        "jvm_memory_used_bytes",
        'jvm_memory_used_bytes{job="besu"}',
        start=start,
        end=start + timedelta(seconds=15),
        step_seconds=15,
    )

    assert len(samples) == 2
    assert samples[0].labels["area"] == "heap"
    assert samples[1].value == 110.0
    assert "/api/v1/query_range?" in captured_url[0]
    assert "step=15" in captured_url[0]


@pytest.mark.parametrize(
    "data",
    [
        {"resultType": "matrix", "result": "invalid"},
        {"resultType": "vector", "result": []},
    ],
)
def test_query_range_rejects_malformed_response(
    monkeypatch: pytest.MonkeyPatch,
    data: dict[str, object],
) -> None:
    def fake_urlopen(url: str, *, timeout: float) -> BytesIO:
        del url
        del timeout
        return BytesIO(
            json.dumps({"status": "success", "data": data}).encode("utf-8")
        )

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    observer = PrometheusObserver("http://127.0.0.1:9090")
    now = datetime.now(UTC)

    with pytest.raises(RuntimeError, match="invalid Prometheus range"):
        observer._query_range(
            "node_up",
            'up{job="besu"}',
            start=now,
            end=now,
            step_seconds=15,
        )


def test_capture_range_rejects_empty_metric_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observer = PrometheusObserver("http://127.0.0.1:9090")
    monkeypatch.setattr(observer, "_query_range", lambda *args, **kwargs: ())
    now = datetime.now(UTC)

    with pytest.raises(RuntimeError, match="returned no samples"):
        observer.capture_range(now, now)


def test_write_prometheus_timeseries_csv_has_required_columns(
    tmp_path: Path,
) -> None:
    sample = PrometheusTimeSeriesSample(
        timestamp=datetime(2026, 8, 14, 12, 0, tzinfo=UTC),
        metric_name="jvm_memory_used_bytes",
        instance="validator-1:9545",
        labels={"instance": "validator-1:9545", "area": "heap"},
        value=1024.0,
    )

    path = write_prometheus_timeseries("run-001", (sample,), tmp_path)
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert path.name == "metrics-timeseries-run-001.csv"
    assert rows[0].keys() == {
        "timestamp",
        "metric_name",
        "instance",
        "labels",
        "value",
    }
    assert json.loads(rows[0]["labels"])["area"] == "heap"
