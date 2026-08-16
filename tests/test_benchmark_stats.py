"""Tests for benchmark statistics."""

from datetime import UTC, datetime, timedelta

import pytest

from blockchain_client.benchmark_models import (
    BenchmarkRunResult,
    BenchmarkScenario,
    BenchmarkTransactionResult,
)
from blockchain_client.benchmark_stats import percentile, summarize_run


def make_transaction(
    *,
    sequence: int,
    latency_seconds: float,
    success: bool = True,
    block_number: int | None = 100,
    gas_used: int | None = 70_000,
) -> BenchmarkTransactionResult:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    return BenchmarkTransactionResult(
        sequence=sequence,
        operation="recordEvidence",
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=latency_seconds),
        success=success,
        tx_hash=("0x" + f"{sequence:064x}") if success else None,
        block_number=block_number if success else None,
        gas_used=gas_used if success else None,
        confirmations=1 if success else None,
        error_type=None if success else "TransactionSubmissionError",
        error_message=None if success else "synthetic failure",
    )


def make_run(
    transactions: tuple[BenchmarkTransactionResult, ...],
    duration_seconds: float = 10.0,
) -> BenchmarkRunResult:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    scenario = BenchmarkScenario(
        name="evidence-c2",
        operation="recordEvidence",
        transaction_count=len(transactions),
        concurrency=min(2, len(transactions)),
        confirmations=1,
    )

    return BenchmarkRunResult(
        run_id="run-001",
        scenario=scenario,
        repetition=1,
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=duration_seconds),
        transactions=transactions,
    )


@pytest.mark.parametrize(
    ("percentile_value", "expected"),
    [
        (0, 1.0),
        (50, 2.5),
        (100, 4.0),
    ],
)
def test_percentile_calculates_interpolated_values(
    percentile_value: float,
    expected: float,
) -> None:
    assert percentile([1.0, 2.0, 3.0, 4.0], percentile_value) == pytest.approx(expected)


def test_percentile_returns_none_for_empty_values() -> None:
    assert percentile([], 50) is None


def test_percentile_rejects_invalid_percentile() -> None:
    with pytest.raises(ValueError, match="between 0 and 100"):
        percentile([1.0], 101)


def test_summary_calculates_success_and_throughput() -> None:
    run = make_run(
        (
            make_transaction(sequence=1, latency_seconds=2),
            make_transaction(sequence=2, latency_seconds=4),
            make_transaction(sequence=3, latency_seconds=3, success=False),
        ),
        duration_seconds=10,
    )

    summary = summarize_run(run)

    assert summary.submitted == 3
    assert summary.successful == 2
    assert summary.failed == 1

    assert summary.success_rate == pytest.approx(2 / 3)
    assert summary.failure_rate == pytest.approx(1 / 3)

    assert summary.throughput_tps == pytest.approx(0.2)


def test_summary_calculates_latency_statistics() -> None:
    run = make_run(
        (
            make_transaction(sequence=1, latency_seconds=1),
            make_transaction(sequence=2, latency_seconds=2),
            make_transaction(sequence=3, latency_seconds=3),
            make_transaction(sequence=4, latency_seconds=4),
        )
    )

    summary = summarize_run(run)

    assert summary.latency_min_seconds == 1
    assert summary.latency_mean_seconds == pytest.approx(2.5)
    assert summary.latency_p50_seconds == pytest.approx(2.5)
    assert summary.latency_p95_seconds == pytest.approx(3.85)
    assert summary.latency_p99_seconds == pytest.approx(3.97)
    assert summary.latency_max_seconds == 4


def test_summary_ignores_failed_transaction_latency() -> None:
    run = make_run(
        (
            make_transaction(sequence=1, latency_seconds=2),
            make_transaction(
                sequence=2,
                latency_seconds=100,
                success=False,
            ),
        )
    )

    summary = summarize_run(run)

    assert summary.latency_mean_seconds == 2


def test_summary_calculates_gas_statistics() -> None:
    run = make_run(
        (
            make_transaction(
                sequence=1,
                latency_seconds=1,
                gas_used=70_000,
            ),
            make_transaction(
                sequence=2,
                latency_seconds=1,
                gas_used=80_000,
            ),
        )
    )

    summary = summarize_run(run)

    assert summary.gas_total == 150_000
    assert summary.gas_mean == pytest.approx(75_000)


def test_summary_calculates_block_distribution() -> None:
    run = make_run(
        (
            make_transaction(
                sequence=1,
                latency_seconds=1,
                block_number=100,
            ),
            make_transaction(
                sequence=2,
                latency_seconds=1,
                block_number=100,
            ),
            make_transaction(
                sequence=3,
                latency_seconds=1,
                block_number=101,
            ),
        )
    )

    summary = summarize_run(run)

    assert summary.first_block == 100
    assert summary.last_block == 101
    assert summary.blocks_used == 2
    assert summary.transactions_per_block == pytest.approx(1.5)