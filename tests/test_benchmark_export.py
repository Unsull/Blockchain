"""Tests for benchmark result export."""

import csv
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from blockchain_client.benchmark_export import export_run_bundle
from blockchain_client.benchmark_models import (
    BenchmarkRunResult,
    BenchmarkScenario,
    BenchmarkTransactionResult,
)
from blockchain_client.benchmark_stats import summarize_run


def make_run() -> BenchmarkRunResult:
    started_at = datetime(
        2026,
        8,
        12,
        8,
        0,
        tzinfo=UTC,
    )

    scenario = BenchmarkScenario(
        name="evidence-c1",
        operation="recordEvidence",
        transaction_count=2,
        concurrency=1,
        confirmations=1,
    )

    transactions = (
        BenchmarkTransactionResult(
            sequence=1,
            operation="recordEvidence",
            started_at=started_at,
            finished_at=started_at
            + timedelta(seconds=2),
            success=True,
            tx_hash="0x" + "01" * 32,
            block_number=100,
            gas_used=70_000,
            effective_gas_price=1,
            confirmations=1,
        ),
        BenchmarkTransactionResult(
            sequence=2,
            operation="recordEvidence",
            started_at=started_at
            + timedelta(seconds=2),
            finished_at=started_at
            + timedelta(seconds=5),
            success=True,
            tx_hash="0x" + "02" * 32,
            block_number=101,
            gas_used=71_000,
            effective_gas_price=1,
            confirmations=1,
        ),
    )

    return BenchmarkRunResult(
        run_id="run-001",
        scenario=scenario,
        repetition=1,
        started_at=started_at,
        finished_at=started_at
        + timedelta(seconds=5),
        transactions=transactions,
    )


def test_export_run_bundle_creates_expected_files(
    tmp_path: Path,
) -> None:
    run = make_run()
    summary = summarize_run(run)

    paths = export_run_bundle(
        run,
        summary,
        tmp_path,
    )

    assert paths.run_json.exists()
    assert paths.transactions_csv.exists()
    assert paths.summary_json.exists()


def test_export_run_json_contains_raw_transactions(
    tmp_path: Path,
) -> None:
    run = make_run()

    paths = export_run_bundle(
        run,
        summarize_run(run),
        tmp_path,
    )

    payload = json.loads(
        paths.run_json.read_text(
            encoding="utf-8"
        )
    )

    assert payload["run_id"] == "run-001"
    assert payload["scenario"]["name"] == "evidence-c1"
    assert len(payload["transactions"]) == 2
    assert payload["transactions"][0]["latency_seconds"] == 2.0


def test_export_summary_json_contains_statistics(
    tmp_path: Path,
) -> None:
    run = make_run()

    paths = export_run_bundle(
        run,
        summarize_run(run),
        tmp_path,
    )

    payload = json.loads(
        paths.summary_json.read_text(
            encoding="utf-8"
        )
    )

    assert payload["submitted"] == 2
    assert payload["successful"] == 2
    assert payload["failed"] == 0
    assert payload["throughput_tps"] == 0.4


def test_export_transactions_csv_contains_one_row_per_transaction(
    tmp_path: Path,
) -> None:
    run = make_run()

    paths = export_run_bundle(
        run,
        summarize_run(run),
        tmp_path,
    )

    with paths.transactions_csv.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    assert len(rows) == 2
    assert rows[0]["sequence"] == "1"
    assert rows[0]["scenario_name"] == "evidence-c1"
    assert rows[1]["sequence"] == "2"