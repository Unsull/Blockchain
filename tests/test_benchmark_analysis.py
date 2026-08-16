from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from blockchain_client.benchmark_analysis import (
    aggregate_summaries,
    analyze_network_observations,
    load_network_observations,
    load_summary_files,
    validate_expected_matrix,
    write_aggregate_csv,
    write_aggregate_json,
    write_markdown_report,
)


def make_network_observation(
    *,
    run_id: str = "run-1",
    before_heights: tuple[int, ...] = (100, 100, 100, 100, 100),
    after_heights: tuple[int, ...] = (102, 102, 102, 102, 102),
    up_values: tuple[int, ...] = (1, 1, 1, 1, 1),
    sync_values: tuple[int, ...] = (1, 1, 1, 1, 1),
    peer_values: tuple[int, ...] = (4, 4, 4, 4, 4),
) -> dict[str, object]:
    instances = ["rpc-node", "validator-1", "validator-2", "validator-3", "validator-4"]

    def samples(values: tuple[int, ...]) -> list[dict[str, object]]:
        return [
            {"instance": f"{instance}:9545", "value": float(value)}
            for instance, value in zip(instances, values, strict=True)
        ]

    def snapshot(heights: tuple[int, ...]) -> dict[str, object]:
        return {
            "captured_at": "2026-08-14T00:00:00+00:00",
            "metrics": {
                "node_up": samples(up_values),
                "sync_status": samples(sync_values),
                "peer_count": samples(peer_values),
                "block_height": samples(heights),
            },
        }

    return {
        "run_id": run_id,
        "before": snapshot(before_heights),
        "after": snapshot(after_heights),
    }


def make_summary(
    *,
    scenario_name: str,
    operation: str,
    concurrency: int,
    repetition: int,
    throughput: float,
    p50: float = 10.0,
    p95: float = 10.1,
    p99: float = 10.2,
    gas_mean: float = 100.0,
    submitted: int = 20,
    successful: int = 20,
    failed: int = 0,
) -> dict[str, object]:
    return {
        "run_id": f"{scenario_name}-{repetition}",
        "scenario_name": scenario_name,
        "operation": operation,
        "repetition": repetition,
        "concurrency": concurrency,
        "submitted": submitted,
        "successful": successful,
        "failed": failed,
        "duration_seconds": 100.0,
        "throughput_tps": throughput,
        "success_rate": (
            successful / submitted
        ),
        "failure_rate": (
            failed / submitted
        ),
        "latency_min_seconds": 9.0,
        "latency_mean_seconds": 10.0,
        "latency_p50_seconds": p50,
        "latency_p95_seconds": p95,
        "latency_p99_seconds": p99,
        "latency_max_seconds": 10.5,
        "gas_total": int(gas_mean * successful),
        "gas_mean": gas_mean,
    }


def test_aggregate_summaries() -> None:
    summaries = [
        make_summary(
            scenario_name="evidence-c2",
            operation="recordEvidence",
            concurrency=2,
            repetition=1,
            throughput=0.20,
            gas_mean=73_830.0,
        ),
        make_summary(
            scenario_name="evidence-c2",
            operation="recordEvidence",
            concurrency=2,
            repetition=2,
            throughput=0.21,
            gas_mean=73_832.0,
        ),
        make_summary(
            scenario_name="evidence-c2",
            operation="recordEvidence",
            concurrency=2,
            repetition=3,
            throughput=0.19,
            gas_mean=73_834.0,
        ),
    ]

    results = aggregate_summaries(summaries)

    assert len(results) == 1

    result = results[0]

    assert result.scenario_name == "evidence-c2"
    assert result.operation == "recordEvidence"
    assert result.concurrency == 2
    assert result.repetitions == 3
    assert result.submitted == 60
    assert result.successful == 60
    assert result.failed == 0
    assert result.success_rate == pytest.approx(1.0)
    assert result.failure_rate == pytest.approx(0.0)
    assert result.mean_throughput_tps == pytest.approx(0.20)
    assert result.stddev_throughput_tps == pytest.approx(0.01)
    assert result.mean_gas == pytest.approx(73_832.0)


def test_aggregate_rejects_inconsistent_totals() -> None:
    summary = make_summary(
        scenario_name="evidence-c1",
        operation="recordEvidence",
        concurrency=1,
        repetition=1,
        throughput=0.1,
        successful=19,
        failed=0,
    )

    with pytest.raises(
        ValueError,
        match="inconsistent transaction totals",
    ):
        aggregate_summaries([summary])


def test_load_summary_files(tmp_path: Path) -> None:
    payload = make_summary(
        scenario_name="access-c1",
        operation="recordAccess",
        concurrency=1,
        repetition=1,
        throughput=0.1,
    )

    path = tmp_path / "summary-test.json"
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    loaded = load_summary_files(tmp_path)

    assert loaded == [payload]


def test_load_summary_files_rejects_empty_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="no benchmark summary files found",
    ):
        load_summary_files(tmp_path)


def test_load_and_analyze_valid_network_observation(tmp_path: Path) -> None:
    payload = make_network_observation(
        before_heights=(100, 101, 100, 100, 100),
        after_heights=(103, 104, 103, 103, 103),
        peer_values=(2, 4, 4, 3, 4),
    )
    (tmp_path / "network-run-1.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    observations = load_network_observations(tmp_path)
    health = analyze_network_observations(
        observations,
        expected_run_ids={"run-1"},
    )

    assert len(observations) == 1
    assert health.observation_count == 1
    assert health.before_node_up_samples == 5
    assert health.after_node_up_samples == 5
    assert health.all_expected_targets_up is True
    assert health.all_nodes_synchronized is True
    assert health.minimum_peer_count == 2
    assert health.maximum_peer_count == 4
    assert health.maximum_block_height_divergence == 1
    assert health.all_observations_progressed is True


def test_load_network_observations_allows_missing_files(
    tmp_path: Path,
) -> None:
    assert load_network_observations(tmp_path) == []


def test_network_analysis_detects_down_and_unsynchronized_node(
    tmp_path: Path,
) -> None:
    payload = make_network_observation(
        up_values=(1, 1, 0, 1, 1),
        sync_values=(1, 1, 1, 0, 1),
        before_heights=(100, 100, 102, 100, 100),
        after_heights=(100, 100, 102, 100, 100),
    )
    (tmp_path / "network-run-1.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    health = analyze_network_observations(
        load_network_observations(tmp_path)
    )

    assert health.all_expected_targets_up is False
    assert health.all_nodes_synchronized is False
    assert health.maximum_block_height_divergence == 2
    assert health.all_observations_progressed is False


def test_validate_expected_matrix() -> None:
    summaries: list[dict[str, object]] = []

    scenarios = [
        ("evidence-c1", "recordEvidence", 1),
        ("evidence-c2", "recordEvidence", 2),
        ("evidence-c5", "recordEvidence", 5),
        ("evidence-c10", "recordEvidence", 10),
        ("access-c1", "recordAccess", 1),
        ("access-c2", "recordAccess", 2),
        ("access-c5", "recordAccess", 5),
        ("access-c10", "recordAccess", 10),
    ]

    for name, operation, concurrency in scenarios:
        for repetition in range(1, 4):
            summaries.append(
                make_summary(
                    scenario_name=name,
                    operation=operation,
                    concurrency=concurrency,
                    repetition=repetition,
                    throughput=float(concurrency) / 10.0,
                )
            )

    results = aggregate_summaries(summaries)

    validate_expected_matrix(results)


def test_validate_expected_matrix_rejects_partial_data() -> None:
    summaries = [
        make_summary(
            scenario_name="evidence-c1",
            operation="recordEvidence",
            concurrency=1,
            repetition=repetition,
            throughput=0.1,
        )
        for repetition in range(1, 4)
    ]

    results = aggregate_summaries(summaries)

    with pytest.raises(
        ValueError,
        match="benchmark matrix does not match expected scenarios",
    ):
        validate_expected_matrix(results)


def test_exports(
    tmp_path: Path,
) -> None:
    summaries = [
        make_summary(
            scenario_name="access-c5",
            operation="recordAccess",
            concurrency=5,
            repetition=repetition,
            throughput=0.5,
            gas_mean=99_010.0,
        )
        for repetition in range(1, 4)
    ]

    results = aggregate_summaries(summaries)

    csv_path = tmp_path / "aggregate.csv"
    json_path = tmp_path / "aggregate.json"
    report_path = tmp_path / "benchmark-report.md"

    write_aggregate_csv(results, csv_path)
    write_aggregate_json(results, json_path)
    network_path = tmp_path / "network-access-c5-1.json"
    network_path.write_text(
        json.dumps(make_network_observation()),
        encoding="utf-8",
    )
    network_health = analyze_network_observations(
        load_network_observations(tmp_path)
    )
    write_markdown_report(results, report_path, network_health)

    assert csv_path.exists()
    assert json_path.exists()
    assert report_path.exists()

    with csv_path.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1
    assert rows[0]["scenario_name"] == "access-c5"

    json_payload = json.loads(
        json_path.read_text(encoding="utf-8")
    )

    assert json_payload[0]["concurrency"] == 5

    report = report_path.read_text(encoding="utf-8")

    assert "# Benchmark Performance Evaluation" in report
    assert "recordAccess" in report
    assert "60" in report
    assert "## Network Health During Benchmark" in report
    assert "All expected five Besu targets were UP" in report
    assert "highest observed throughput" in report
    assert "maximum TPS" not in report
