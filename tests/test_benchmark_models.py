"""Tests for benchmark data models."""

from datetime import UTC, datetime, timedelta

import pytest

from blockchain_client.benchmark_models import (
    BenchmarkOperation,
    BenchmarkRunResult,
    BenchmarkScenario,
    BenchmarkTransactionResult,
)


def make_successful_transaction(
    sequence: int = 1,
    operation: BenchmarkOperation = "recordEvidence",
) -> BenchmarkTransactionResult:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    return BenchmarkTransactionResult(
        sequence=sequence,
        operation=operation,
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=5),
        success=True,
        tx_hash="0x" + "ab" * 32,
        block_number=100,
        gas_used=73_835,
        effective_gas_price=1,
        confirmations=1,
    )


def test_scenario_validation_accepts_valid_configuration() -> None:
    scenario = BenchmarkScenario(
        name="evidence-c1",
        operation="recordEvidence",
        transaction_count=5,
        concurrency=1,
        confirmations=1,
    )

    scenario.validate()


@pytest.mark.parametrize(
    ("transaction_count", "concurrency"),
    [
        (0, 1),
        (5, 0),
        (2, 3),
    ],
)
def test_scenario_validation_rejects_invalid_counts(
    transaction_count: int,
    concurrency: int,
) -> None:
    scenario = BenchmarkScenario(
        name="invalid",
        operation="recordEvidence",
        transaction_count=transaction_count,
        concurrency=concurrency,
        confirmations=1,
    )

    with pytest.raises(ValueError):
        scenario.validate()


def test_transaction_latency_is_calculated_from_timestamps() -> None:
    transaction = make_successful_transaction()

    assert transaction.latency_seconds == 5.0


def test_failed_transaction_requires_error_type() -> None:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    transaction = BenchmarkTransactionResult(
        sequence=1,
        operation="recordEvidence",
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=1),
        success=False,
    )

    with pytest.raises(ValueError, match="error_type"):
        transaction.validate()


def test_run_validation_requires_expected_transaction_count() -> None:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    scenario = BenchmarkScenario(
        name="evidence-c1",
        operation="recordEvidence",
        transaction_count=2,
        concurrency=1,
        confirmations=1,
    )

    run = BenchmarkRunResult(
        run_id="run-001",
        scenario=scenario,
        repetition=1,
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=10),
        transactions=(make_successful_transaction(),),
    )

    with pytest.raises(ValueError, match="transaction result count"):
        run.validate()


def test_run_validation_accepts_consistent_result() -> None:
    started_at = datetime(2026, 8, 12, 8, 0, tzinfo=UTC)

    scenario = BenchmarkScenario(
        name="evidence-c1",
        operation="recordEvidence",
        transaction_count=2,
        concurrency=1,
        confirmations=1,
    )

    run = BenchmarkRunResult(
        run_id="run-001",
        scenario=scenario,
        repetition=1,
        started_at=started_at,
        finished_at=started_at + timedelta(seconds=10),
        transactions=(
            make_successful_transaction(sequence=1),
            make_successful_transaction(sequence=2),
        ),
    )

    run.validate()

    assert run.duration_seconds == 10.0