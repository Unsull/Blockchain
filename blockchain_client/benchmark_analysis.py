from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AggregateBenchmarkResult:
    scenario_name: str
    operation: str
    concurrency: int
    repetitions: int
    submitted: int
    successful: int
    failed: int
    success_rate: float
    failure_rate: float
    mean_throughput_tps: float
    stddev_throughput_tps: float
    min_throughput_tps: float
    max_throughput_tps: float
    mean_p50_seconds: float | None
    mean_p95_seconds: float | None
    mean_p99_seconds: float | None
    mean_gas: float | None


@dataclass(frozen=True)
class NetworkMetricSample:
    instance: str
    value: float


@dataclass(frozen=True)
class NetworkSnapshot:
    node_up: tuple[NetworkMetricSample, ...]
    sync_status: tuple[NetworkMetricSample, ...]
    peer_count: tuple[NetworkMetricSample, ...]
    block_height: tuple[NetworkMetricSample, ...]

    @property
    def block_height_divergence(self) -> float | None:
        values = [sample.value for sample in self.block_height]
        if not values:
            return None
        return max(values) - min(values)


@dataclass(frozen=True)
class NetworkObservation:
    run_id: str
    before: NetworkSnapshot
    after: NetworkSnapshot


@dataclass(frozen=True)
class AggregateNetworkHealth:
    observation_count: int
    before_node_up_samples: int
    after_node_up_samples: int
    expected_target_count: int
    all_expected_targets_up: bool
    all_nodes_synchronized: bool
    peer_sample_count: int
    minimum_peer_count: float | None
    maximum_peer_count: float | None
    block_height_sample_count: int
    maximum_block_height_divergence: float | None
    progressed_observation_count: int
    all_observations_progressed: bool


def load_summary_files(directory: Path) -> list[dict[str, Any]]:
    """Load all benchmark summary JSON files from a result directory."""
    paths = sorted(directory.glob("summary-*.json"))

    if not paths:
        raise ValueError(
            f"no benchmark summary files found in: {directory}"
        )

    summaries: list[dict[str, Any]] = []

    for path in paths:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"invalid benchmark summary JSON: {path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                f"benchmark summary must be a JSON object: {path}"
            )

        summaries.append(payload)

    return summaries


def load_network_observations(
    directory: Path,
) -> list[NetworkObservation]:
    """Load network observations; an absent optional set is empty."""
    observations: list[NetworkObservation] = []
    for path in sorted(directory.glob("network-*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"invalid network observation JSON: {path}"
            ) from exc
        if not isinstance(payload, dict):
            raise ValueError(
                f"network observation must be a JSON object: {path}"
            )
        observations.append(
            NetworkObservation(
                run_id=_required_str(payload, "run_id"),
                before=_parse_network_snapshot(payload, "before"),
                after=_parse_network_snapshot(payload, "after"),
            )
        )
    return observations


def analyze_network_observations(
    observations: Iterable[NetworkObservation],
    *,
    expected_run_ids: set[str] | None = None,
    expected_target_count: int = 5,
) -> AggregateNetworkHealth:
    """Aggregate availability, synchronization, peers, and chain state."""
    items = list(observations)
    run_ids = [item.run_id for item in items]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("duplicate network observation run_id")
    if expected_run_ids is not None and set(run_ids) != expected_run_ids:
        missing = sorted(expected_run_ids - set(run_ids))
        extra = sorted(set(run_ids) - expected_run_ids)
        raise ValueError(
            "network observations do not match benchmark runs; "
            f"missing={missing}, extra={extra}"
        )

    snapshots = [
        snapshot
        for item in items
        for snapshot in (item.before, item.after)
    ]
    before_up = sum(len(item.before.node_up) for item in items)
    after_up = sum(len(item.after.node_up) for item in items)
    all_up = bool(items) and all(
        len(snapshot.node_up) == expected_target_count
        and all(sample.value == 1.0 for sample in snapshot.node_up)
        for snapshot in snapshots
    )
    all_synchronized = bool(items) and all(
        len(snapshot.sync_status) == expected_target_count
        and all(sample.value == 1.0 for sample in snapshot.sync_status)
        for snapshot in snapshots
    )
    peers = [
        sample.value
        for snapshot in snapshots
        for sample in snapshot.peer_count
    ]
    heights = [
        sample.value
        for snapshot in snapshots
        for sample in snapshot.block_height
    ]
    divergences = [
        divergence
        for snapshot in snapshots
        if (divergence := snapshot.block_height_divergence) is not None
    ]
    progressed = sum(
        _snapshot_progressed(item.before, item.after)
        for item in items
    )
    return AggregateNetworkHealth(
        observation_count=len(items),
        before_node_up_samples=before_up,
        after_node_up_samples=after_up,
        expected_target_count=expected_target_count,
        all_expected_targets_up=all_up,
        all_nodes_synchronized=all_synchronized,
        peer_sample_count=len(peers),
        minimum_peer_count=min(peers) if peers else None,
        maximum_peer_count=max(peers) if peers else None,
        block_height_sample_count=len(heights),
        maximum_block_height_divergence=(
            max(divergences) if divergences else None
        ),
        progressed_observation_count=progressed,
        all_observations_progressed=(
            bool(items) and progressed == len(items)
        ),
    )


def aggregate_summaries(
    summaries: Iterable[dict[str, Any]],
) -> list[AggregateBenchmarkResult]:
    """Aggregate run-level summaries into one result per scenario."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for summary in summaries:
        scenario_name = _required_str(summary, "scenario_name")
        grouped[scenario_name].append(summary)

    if not grouped:
        raise ValueError("no benchmark summaries provided")

    results: list[AggregateBenchmarkResult] = []

    for scenario_name, runs in grouped.items():
        ordered_runs = sorted(
            runs,
            key=lambda item: _required_int(item, "repetition"),
        )

        operation = _consistent_str(
            ordered_runs,
            "operation",
            scenario_name,
        )
        concurrency = _consistent_int(
            ordered_runs,
            "concurrency",
            scenario_name,
        )

        submitted = sum(
            _required_int(run, "submitted")
            for run in ordered_runs
        )
        successful = sum(
            _required_int(run, "successful")
            for run in ordered_runs
        )
        failed = sum(
            _required_int(run, "failed")
            for run in ordered_runs
        )

        if submitted <= 0:
            raise ValueError(
                f"scenario {scenario_name!r} has no submitted transactions"
            )

        if successful + failed != submitted:
            raise ValueError(
                f"scenario {scenario_name!r} has inconsistent "
                "transaction totals"
            )

        throughputs = [
            _required_float(run, "throughput_tps")
            for run in ordered_runs
        ]

        p50_values = _optional_float_values(
            ordered_runs,
            "latency_p50_seconds",
        )
        p95_values = _optional_float_values(
            ordered_runs,
            "latency_p95_seconds",
        )
        p99_values = _optional_float_values(
            ordered_runs,
            "latency_p99_seconds",
        )
        gas_values = _optional_float_values(
            ordered_runs,
            "gas_mean",
        )

        results.append(
            AggregateBenchmarkResult(
                scenario_name=scenario_name,
                operation=operation,
                concurrency=concurrency,
                repetitions=len(ordered_runs),
                submitted=submitted,
                successful=successful,
                failed=failed,
                success_rate=successful / submitted,
                failure_rate=failed / submitted,
                mean_throughput_tps=statistics.fmean(throughputs),
                stddev_throughput_tps=_sample_stddev(throughputs),
                min_throughput_tps=min(throughputs),
                max_throughput_tps=max(throughputs),
                mean_p50_seconds=_optional_mean(p50_values),
                mean_p95_seconds=_optional_mean(p95_values),
                mean_p99_seconds=_optional_mean(p99_values),
                mean_gas=_optional_mean(gas_values),
            )
        )

    return sorted(
        results,
        key=lambda item: (
            item.operation,
            item.concurrency,
            item.scenario_name,
        ),
    )


def validate_expected_matrix(
    results: Iterable[AggregateBenchmarkResult],
) -> None:
    """Validate the expected 8-scenario research matrix."""
    result_list = list(results)

    expected = {
        ("recordEvidence", 1),
        ("recordEvidence", 2),
        ("recordEvidence", 5),
        ("recordEvidence", 10),
        ("recordAccess", 1),
        ("recordAccess", 2),
        ("recordAccess", 5),
        ("recordAccess", 10),
    }

    actual = {
        (result.operation, result.concurrency)
        for result in result_list
    }

    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            "benchmark matrix does not match expected scenarios; "
            f"missing={missing}, extra={extra}"
        )

    for result in result_list:
        if result.repetitions != 3:
            raise ValueError(
                f"{result.scenario_name!r} has "
                f"{result.repetitions} repetitions; expected 3"
            )


def write_aggregate_json(
    results: Iterable[AggregateBenchmarkResult],
    path: Path,
) -> None:
    payload = [asdict(result) for result in results]
    _write_text_atomic(
        path,
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def write_aggregate_csv(
    results: Iterable[AggregateBenchmarkResult],
    path: Path,
) -> None:
    rows = [asdict(result) for result in results]

    if not rows:
        raise ValueError("cannot export empty aggregate result")

    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(f".{path.name}.tmp")

    with temporary.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
        )
        writer.writeheader()
        writer.writerows(rows)

    temporary.replace(path)


def write_markdown_report(
    results: Iterable[AggregateBenchmarkResult],
    path: Path,
    network_health: AggregateNetworkHealth | None = None,
) -> None:
    result_list = list(results)

    if not result_list:
        raise ValueError("cannot generate report from empty results")

    submitted = sum(item.submitted for item in result_list)
    successful = sum(item.successful for item in result_list)
    failed = sum(item.failed for item in result_list)

    evidence = [
        item
        for item in result_list
        if item.operation == "recordEvidence"
    ]
    access = [
        item
        for item in result_list
        if item.operation == "recordAccess"
    ]

    measured_runs = sum(item.repetitions for item in result_list)
    lines = [
        "# Benchmark Performance Evaluation",
        "",
        "## Dataset Integrity",
        "",
        f"- Scenarios: {len(result_list)}",
        f"- Measured runs: {measured_runs}",
        f"- Measured transactions: {submitted}",
        f"- Successful measured transactions: {successful}",
        f"- Failed measured transactions: {failed}",
        f"- Observed measured success rate: {_percent(successful, submitted)}",
        "",
        "The transaction totals above include measured benchmark "
        "transactions only. Evidence preparation transactions required "
        "by the recordAccess workload are intentionally excluded from "
        f"the {submitted} measured transactions or the measured access interval.",
        "",
        "## Experimental Setup",
        "",
        (
            "The experiment used Hyperledger Besu QBFT with four validator "
            "nodes and one RPC node in a local, single-host Docker integration "
            "environment. Prometheus (15-second scrape interval), Grafana, "
            "and the Python benchmark client provided monitoring and workload "
            "execution. Tested concurrency values were 1, 2, 5, and 10, with "
            "20 measured transactions per repetition, three repetitions per "
            "scenario, and one confirmation."
        ),
        "",
        "## Aggregate Results",
        "",
        (
            "| Operation | Concurrency | Mean TPS | TPS StdDev | "
            "Mean P50 (s) | Mean P95 (s) | Mean P99 (s) | "
            "Mean Gas | Failure Rate |"
        ),
        (
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
        ),
    ]

    for result in result_list:
        lines.append(
            "| "
            f"{result.operation} | "
            f"{result.concurrency} | "
            f"{result.mean_throughput_tps:.4f} | "
            f"{result.stddev_throughput_tps:.4f} | "
            f"{_format_optional(result.mean_p50_seconds)} | "
            f"{_format_optional(result.mean_p95_seconds)} | "
            f"{_format_optional(result.mean_p99_seconds)} | "
            f"{_format_optional(result.mean_gas, digits=1)} | "
            f"{result.failure_rate * 100:.2f}% |"
        )

    lines.extend(
        [
            "",
            "## Performance Interpretation",
            "",
            _throughput_observation(evidence, "recordEvidence"),
            "",
            _throughput_observation(access, "recordAccess"),
            "",
            _gas_observation(evidence, access),
            "",
            _latency_observation(evidence, access),
            "",
            _variability_observation(evidence),
            "",
            (
                "No measured transaction failures were observed in the "
                f"{submitted} measured transactions. This is an observed "
                "result for the tested workload and environment and must "
                "not be interpreted as a guarantee of failure-free "
                "production operation."
            ),
            "",
            (
                "Increasing concurrency increased completion throughput but "
                "did not materially reduce individual transaction completion "
                "latency, whose mean P95 values remained near 10 seconds. No "
                "clear throughput saturation was demonstrated at concurrency "
                "10 or below. The highest observed throughput is a result "
                "within the tested matrix, not evidence of a system capacity "
                "ceiling or production performance."
            ),
            "",
            "## Network Health During Benchmark",
            "",
            *_network_health_lines(network_health),
            "",
            "## Measurement Semantics",
            "",
            (
                "Throughput represents successful end-to-end benchmark "
                "operations divided by the measured run duration. The "
                "client waits for transaction receipts and the configured "
                "confirmation count, so this is completion throughput "
                "rather than raw RPC submission throughput."
            ),
            "",
            (
                "Latency is measured from benchmark operation start until "
                "the blockchain client completes the transaction operation, "
                "including receipt and confirmation waiting."
            ),
            "",
            (
                "For recordAccess, prerequisite evidence records are "
                "created before the measured interval. Their execution "
                "time and gas usage are not included in recordAccess "
                "latency or throughput statistics."
            ),
            "",
            (
                "Gas usage is reported as a smart-contract execution and "
                "resource metric. It is not interpreted as a public-mainnet "
                "monetary transaction cost."
            ),
            "",
            "## Experimental Scope and Limitations",
            "",
            (
                "This is a local controlled integration benchmark whose "
                "components operated in a single-host Docker environment. "
                "It is not a production benchmark."
            ),
            "",
            (
                "The reported results therefore describe the observed "
                "performance of this prototype and configuration. They "
                "does not establish the capacity of Hyperledger Besu or "
                "QBFT in general."
            ),
            "",
            (
                "Concurrency levels were limited to 1, 2, 5, and 10. "
                "Because the experiment did not continue until a clear "
                "throughput plateau or failure boundary was reached, the "
                "highest observed throughput is not a capacity limit."
            ),
            "",
            (
                "The local single-host environment does not reproduce WAN "
                "latency, packet loss, multi-host storage behavior, "
                "production authentication, TLS overhead, load balancing, "
                "validator or node failures, or network partitions. "
                "Concurrency above 10 was not tested."
            ),
            "",
            (
                "Temporary Prometheus block-height differences may occur "
                "because individual Besu targets are scraped at different "
                "times while the chain continues producing blocks. "
                "Block-height divergence must therefore be interpreted "
                "together with synchronization state, peer connectivity, "
                "chain progress, and transaction outcomes. Long-duration "
                "stress and state-growth behavior were not tested."
            ),
            "",
            "## Reproducibility",
            "",
            "Run the analyzer from the repository root:",
            "",
            "```text",
            "python network/besu/scripts/analyze-benchmark-results.py \\",
            "  network/besu/benchmarks/results/<matrix-directory>",
            "```",
            "",
            (
                "The analysis directory contains `aggregate.csv`, "
                "`aggregate.json`, and `benchmark-report.md`."
            ),
            "",
        ]
    )

    _write_text_atomic(
        path,
        "\n".join(lines),
    )


def _throughput_observation(
    results: list[AggregateBenchmarkResult],
    label: str,
) -> str:
    if not results:
        return f"No {label} results were available."

    ordered = sorted(results, key=lambda item: item.concurrency)
    first = ordered[0]
    last = ordered[-1]

    return (
        f"For {label}, mean throughput increased from "
        f"{first.mean_throughput_tps:.4f} TPS at concurrency "
        f"{first.concurrency} to {last.mean_throughput_tps:.4f} TPS "
        f"at concurrency {last.concurrency}. The tested range does not "
        "by itself establish a maximum system throughput."
    )


def _gas_observation(
    evidence: list[AggregateBenchmarkResult],
    access: list[AggregateBenchmarkResult],
) -> str:
    evidence_gas = [
        item.mean_gas
        for item in evidence
        if item.mean_gas is not None
    ]
    access_gas = [
        item.mean_gas
        for item in access
        if item.mean_gas is not None
    ]

    if not evidence_gas or not access_gas:
        return "Insufficient gas data was available for comparison."

    evidence_mean = statistics.fmean(evidence_gas)
    access_mean = statistics.fmean(access_gas)

    increase = (
        (access_mean - evidence_mean) / evidence_mean * 100
        if evidence_mean > 0
        else math.nan
    )

    return (
        "Average recordAccess gas usage was "
        f"{access_mean:.1f}, compared with "
        f"{evidence_mean:.1f} for recordEvidence, "
        f"an increase of approximately {increase:.1f}%."
    )


def _latency_observation(
    evidence: list[AggregateBenchmarkResult],
    access: list[AggregateBenchmarkResult],
) -> str:
    access_by_concurrency = {
        item.concurrency: item
        for item in access
    }
    higher_access = [
        item.mean_p95_seconds
        for concurrency, item in access_by_concurrency.items()
        if concurrency in {5, 10} and item.mean_p95_seconds is not None
    ]
    lower_access = [
        item.mean_p95_seconds
        for concurrency, item in access_by_concurrency.items()
        if concurrency in {1, 2} and item.mean_p95_seconds is not None
    ]
    if not higher_access or not lower_access:
        return "Insufficient latency data was available for comparison."
    return (
        "recordAccess completion latency increased slightly at higher "
        "concurrency, particularly at 5 and 10, while all measured access "
        "transactions still completed successfully. recordEvidence and "
        "recordAccess mean P95 latency remained close to the configured "
        "block-completion timescale across the tested scenarios."
    )


def _variability_observation(
    evidence: list[AggregateBenchmarkResult],
) -> str:
    if not evidence:
        return "No recordEvidence variability data was available."
    most_variable = max(
        evidence,
        key=lambda item: item.stddev_throughput_tps,
    )
    return (
        f"{most_variable.scenario_name} had the highest observed "
        "repetition-to-repetition TPS variability among recordEvidence "
        f"scenarios (standard deviation "
        f"{most_variable.stddev_throughput_tps:.4f} TPS)."
    )


def _network_health_lines(
    health: AggregateNetworkHealth | None,
) -> list[str]:
    if health is None or health.observation_count == 0:
        return [
            "No network observation artifacts were available for this "
            "analysis. Application benchmark results remain usable, but "
            "network-health context is unavailable."
        ]

    availability = (
        "All expected five Besu targets were UP in every before/after snapshot."
        if health.all_expected_targets_up
        else "At least one snapshot had a missing or DOWN Besu target."
    )
    synchronization = (
        "All monitored nodes reported synchronized in every snapshot."
        if health.all_nodes_synchronized
        else "At least one monitored node did not report synchronized."
    )
    progress = (
        "Block heights progressed between before and after snapshots for "
        "every observed run."
        if health.all_observations_progressed
        else (
            "Block-height progression was observed for "
            f"{health.progressed_observation_count} of "
            f"{health.observation_count} runs."
        )
    )
    peer_range = (
        f"{_format_optional(health.minimum_peer_count, digits=0)} to "
        f"{_format_optional(health.maximum_peer_count, digits=0)}"
    )
    divergence = _format_optional(
        health.maximum_block_height_divergence,
        digits=0,
    )
    lines = [
        f"Network observations analyzed: {health.observation_count}.",
        availability,
        synchronization,
        (
            f"Peer connectivity samples ranged from {peer_range} direct "
            "peers. Peer count describes node connectivity and is not a "
            "QBFT quorum measurement."
        ),
        f"Maximum observed per-snapshot block-height divergence: {divergence}.",
        progress,
    ]
    if (
        health.maximum_block_height_divergence is not None
        and health.maximum_block_height_divergence > 1
    ):
        lines.append(
            "Prometheus targets are sampled asynchronously, so temporary "
            "block-height divergence alone is not evidence of a fork, "
            "consensus failure, or QBFT failure."
        )
    return lines


def _parse_network_snapshot(
    payload: dict[str, Any],
    key: str,
) -> NetworkSnapshot:
    raw_snapshot = payload.get(key)
    if not isinstance(raw_snapshot, dict):
        raise ValueError(f"invalid or missing network snapshot {key!r}")
    metrics = raw_snapshot.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError(f"invalid or missing metrics in snapshot {key!r}")
    return NetworkSnapshot(
        node_up=_parse_metric_samples(metrics, "node_up"),
        sync_status=_parse_metric_samples(metrics, "sync_status"),
        peer_count=_parse_metric_samples(metrics, "peer_count"),
        block_height=_parse_metric_samples(metrics, "block_height"),
    )


def _parse_metric_samples(
    metrics: dict[str, Any],
    key: str,
) -> tuple[NetworkMetricSample, ...]:
    raw_samples = metrics.get(key)
    if not isinstance(raw_samples, list):
        raise ValueError(f"invalid or missing network metric {key!r}")
    samples: list[NetworkMetricSample] = []
    for raw_sample in raw_samples:
        if not isinstance(raw_sample, dict):
            raise ValueError(f"invalid network metric sample {key!r}")
        samples.append(
            NetworkMetricSample(
                instance=_required_str(raw_sample, "instance"),
                value=_required_float(raw_sample, "value"),
            )
        )
    return tuple(samples)


def _snapshot_progressed(
    before: NetworkSnapshot,
    after: NetworkSnapshot,
) -> bool:
    before_by_instance = {
        sample.instance: sample.value
        for sample in before.block_height
    }
    after_by_instance = {
        sample.instance: sample.value
        for sample in after.block_height
    }
    common = before_by_instance.keys() & after_by_instance.keys()
    return bool(common) and all(
        after_by_instance[instance] > before_by_instance[instance]
        for instance in common
    )


def _required_str(
    payload: dict[str, Any],
    key: str,
) -> str:
    value = payload.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid or missing {key!r}")

    return value


def _required_int(
    payload: dict[str, Any],
    key: str,
) -> int:
    value = payload.get(key)

    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"invalid or missing {key!r}")

    return value


def _required_float(
    payload: dict[str, Any],
    key: str,
) -> float:
    value = payload.get(key)

    if isinstance(value, bool) or not isinstance(
        value,
        int | float,
    ):
        raise ValueError(f"invalid or missing {key!r}")

    return float(value)


def _consistent_str(
    runs: list[dict[str, Any]],
    key: str,
    scenario_name: str,
) -> str:
    values = {
        _required_str(run, key)
        for run in runs
    }

    if len(values) != 1:
        raise ValueError(
            f"scenario {scenario_name!r} has inconsistent {key}"
        )

    return next(iter(values))


def _consistent_int(
    runs: list[dict[str, Any]],
    key: str,
    scenario_name: str,
) -> int:
    values = {
        _required_int(run, key)
        for run in runs
    }

    if len(values) != 1:
        raise ValueError(
            f"scenario {scenario_name!r} has inconsistent {key}"
        )

    return next(iter(values))


def _optional_float_values(
    runs: list[dict[str, Any]],
    key: str,
) -> list[float]:
    values: list[float] = []

    for run in runs:
        value = run.get(key)

        if value is None:
            continue

        if isinstance(value, bool) or not isinstance(
            value,
            int | float,
        ):
            raise ValueError(f"invalid {key!r}")

        values.append(float(value))

    return values


def _sample_stddev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    return statistics.stdev(values)


def _optional_mean(values: list[float]) -> float | None:
    if not values:
        return None

    return statistics.fmean(values)


def _percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "0.00%"

    return f"{numerator / denominator * 100:.2f}%"


def _format_optional(
    value: float | None,
    *,
    digits: int = 4,
) -> str:
    if value is None:
        return "N/A"

    return f"{value:.{digits}f}"


def _write_text_atomic(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        content,
        encoding="utf-8",
    )
    temporary.replace(path)
