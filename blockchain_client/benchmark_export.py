"""Export benchmark results to machine-readable formats."""

import json
from csv import DictWriter
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from blockchain_client.benchmark_models import (
    BenchmarkRunResult,
    BenchmarkSummary,
    BenchmarkTransactionResult,
)


@dataclass(frozen=True)
class BenchmarkExportPaths:
    """Paths produced for one exported benchmark run."""

    run_json: Path
    transactions_csv: Path
    summary_json: Path


def export_run_bundle(
    run: BenchmarkRunResult,
    summary: BenchmarkSummary,
    directory: Path,
) -> BenchmarkExportPaths:
    """Export raw run, transaction CSV, and summary JSON."""

    run.validate()

    if run.run_id != summary.run_id:
        raise ValueError(
            "benchmark run and summary run_id do not match"
        )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    paths = BenchmarkExportPaths(
        run_json=directory / f"run-{run.run_id}.json",
        transactions_csv=directory
        / f"transactions-{run.run_id}.csv",
        summary_json=directory
        / f"summary-{run.run_id}.json",
    )

    _write_json(
        paths.run_json,
        _run_payload(run),
    )

    _write_transactions_csv(
        paths.transactions_csv,
        run,
    )

    _write_json(
        paths.summary_json,
        asdict(summary),
    )

    return paths


def _run_payload(
    run: BenchmarkRunResult,
) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "scenario": asdict(run.scenario),
        "repetition": run.repetition,
        "started_at": run.started_at.isoformat(),
        "finished_at": run.finished_at.isoformat(),
        "duration_seconds": run.duration_seconds,
        "transactions": [
            _transaction_payload(transaction)
            for transaction in run.transactions
        ],
    }


def _transaction_payload(
    transaction: BenchmarkTransactionResult,
) -> dict[str, Any]:
    return {
        "sequence": transaction.sequence,
        "operation": transaction.operation,
        "started_at": transaction.started_at.isoformat(),
        "finished_at": transaction.finished_at.isoformat(),
        "latency_seconds": transaction.latency_seconds,
        "success": transaction.success,
        "tx_hash": transaction.tx_hash,
        "block_number": transaction.block_number,
        "gas_used": transaction.gas_used,
        "effective_gas_price": transaction.effective_gas_price,
        "confirmations": transaction.confirmations,
        "error_type": transaction.error_type,
        "error_message": transaction.error_message,
    }


def _write_transactions_csv(
    path: Path,
    run: BenchmarkRunResult,
) -> None:
    fieldnames = [
        "run_id",
        "scenario_name",
        "repetition",
        "sequence",
        "operation",
        "started_at",
        "finished_at",
        "latency_seconds",
        "success",
        "tx_hash",
        "block_number",
        "gas_used",
        "effective_gas_price",
        "confirmations",
        "error_type",
        "error_message",
    ]

    output = StringIO()

    writer = DictWriter(
        output,
        fieldnames=fieldnames,
        lineterminator="\n",
    )

    writer.writeheader()

    for transaction in run.transactions:
        writer.writerow(
            {
                "run_id": run.run_id,
                "scenario_name": run.scenario.name,
                "repetition": run.repetition,
                **_transaction_payload(transaction),
            }
        )

    _write_text_atomic(
        path,
        output.getvalue(),
    )


def _write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    content = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
    )

    _write_text_atomic(
        path,
        content + "\n",
    )


def _write_text_atomic(
    path: Path,
    content: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = path.with_name(
        f".{path.name}.tmp"
    )

    temporary_path.write_text(
        content,
        encoding="utf-8",
        newline="\n",
    )

    temporary_path.replace(path)