from __future__ import annotations

import argparse
import sys
from pathlib import Path

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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Aggregate benchmark summary artifacts and generate "
            "research-ready result files."
        )
    )
    parser.add_argument(
        "result_directory",
        type=Path,
        help=(
            "Directory containing summary-*.json benchmark artifacts."
        ),
    )
    parser.add_argument(
        "--output-directory",
        type=Path,
        default=None,
        help=(
            "Analysis output directory. Defaults to "
            "<result_directory>/analysis."
        ),
    )
    parser.add_argument(
        "--skip-matrix-validation",
        action="store_true",
        help=(
            "Allow analysis of partial/ad-hoc benchmark datasets."
        ),
    )
    return parser


def execute(args: argparse.Namespace) -> list[Path]:
    result_directory: Path = args.result_directory

    if not result_directory.is_dir():
        raise ValueError(
            f"benchmark result directory does not exist: "
            f"{result_directory}"
        )

    summaries = load_summary_files(result_directory)
    aggregates = aggregate_summaries(summaries)
    observations = load_network_observations(result_directory)

    if not args.skip_matrix_validation:
        validate_expected_matrix(aggregates)
        run_ids = {
            summary["run_id"]
            for summary in summaries
            if isinstance(summary.get("run_id"), str)
        }
        if len(run_ids) != len(summaries):
            raise ValueError("benchmark summaries have invalid run_id values")
        network_health = analyze_network_observations(
            observations,
            expected_run_ids=run_ids,
        )
    else:
        network_health = analyze_network_observations(observations)

    output_directory = (
        args.output_directory
        if args.output_directory is not None
        else result_directory / "analysis"
    )

    csv_path = output_directory / "aggregate.csv"
    json_path = output_directory / "aggregate.json"
    report_path = output_directory / "benchmark-report.md"

    write_aggregate_csv(aggregates, csv_path)
    write_aggregate_json(aggregates, json_path)
    write_markdown_report(
        aggregates,
        report_path,
        network_health,
    )

    return [
        csv_path,
        json_path,
        report_path,
    ]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        paths = execute(args)
    except (OSError, ValueError) as exc:
        print(
            f"benchmark analysis failed: {exc}",
            file=sys.stderr,
        )
        return 1

    print("benchmark analysis completed")
    for path in paths:
        print(path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
