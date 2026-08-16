"""Tests for Prometheus benchmark network observation."""

import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from blockchain_client.benchmark_observer import (
    BenchmarkNetworkObservation,
    BenchmarkNetworkSnapshot,
    PrometheusObserver,
    PrometheusSample,
    write_network_observation,
)


def make_snapshot(
    *,
    node_values: tuple[float, ...] = (1.0, 1.0, 1.0, 1.0, 1.0),
) -> BenchmarkNetworkSnapshot:
    """Create a synthetic network snapshot for validation tests."""

    node_samples = tuple(
        PrometheusSample(
            instance=f"node-{index}:9545",
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