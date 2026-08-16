#!/usr/bin/env python3
"""Run configured EvidenceRegistry benchmark scenarios."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from blockchain_client.benchmark_export import export_run_bundle  # noqa: E402
from blockchain_client.benchmark_observer import (  # noqa: E402
    BenchmarkNetworkObservation,
    PrometheusObserver,
    write_network_observation,
)
from blockchain_client.benchmark_runner import BenchmarkRunner  # noqa: E402
from blockchain_client.benchmark_scenarios import (  # noqa: E402
    BenchmarkScenarioPlan,
    load_scenario_plans,
)
from blockchain_client.benchmark_stats import summarize_run  # noqa: E402
from blockchain_client.client import BlockchainClient  # noqa: E402
from blockchain_client.config import BlockchainClientSettings  # noqa: E402
from blockchain_client.exceptions import BlockchainClientError  # noqa: E402

DEFAULT_SCENARIO_PATH = Path(
    "network/besu/benchmarks/scenarios.json"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "network/besu/benchmarks/results"
)

DEFAULT_ARTIFACT_PATH = Path(
    "out/EvidenceRegistry.sol/EvidenceRegistry.json"
)


def optional_int(
    environment_name: str,
    default: int | None = None,
) -> int | None:
    """Read an optional integer environment variable."""

    value = os.getenv(environment_name)

    if value is None:
        return default

    return int(value)


def build_parser() -> argparse.ArgumentParser:
    """Build the benchmark command-line parser."""

    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--scenario-file",
        type=Path,
        default=DEFAULT_SCENARIO_PATH,
    )

    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenario_names",
        help=(
            "Run only the named scenario. "
            "May be specified multiple times."
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    parser.add_argument(
        "--prometheus-url",
        default=os.getenv(
            "PROMETHEUS_URL",
            "http://127.0.0.1:9090",
        ),
    )

    parser.add_argument(
        "--rpc-url",
        default=os.getenv("RPC_URL"),
    )

    parser.add_argument(
        "--chain-id",
        type=int,
        default=optional_int("CHAIN_ID"),
    )

    parser.add_argument(
        "--contract-address",
        default=os.getenv("CONTRACT_ADDRESS"),
    )

    parser.add_argument(
        "--artifact-path",
        type=Path,
        default=Path(
            os.getenv(
                "ARTIFACT_PATH",
                str(DEFAULT_ARTIFACT_PATH),
            )
        ),
    )

    parser.add_argument(
        "--writer-private-key",
        default=os.getenv("WRITER_PRIVATE_KEY"),
    )

    return parser


def require_configuration(
    args: argparse.Namespace,
) -> None:
    """Validate runtime configuration required for benchmark writes."""

    missing = [
        name
        for name, value in (
            ("rpc-url", args.rpc_url),
            ("chain-id", args.chain_id),
            ("contract-address", args.contract_address),
            ("writer-private-key", args.writer_private_key),
        )
        if value in (None, "")
    ]

    if missing:
        raise ValueError(
            "missing required configuration: "
            + ", ".join(missing)
        )


def select_plans(
    plans: tuple[BenchmarkScenarioPlan, ...],
    names: list[str] | None,
) -> tuple[BenchmarkScenarioPlan, ...]:
    """Return all plans or only explicitly selected scenarios."""

    if not names:
        return plans

    requested = set(names)

    selected = tuple(
        plan
        for plan in plans
        if plan.scenario.name in requested
    )

    found = {
        plan.scenario.name
        for plan in selected
    }

    missing = requested - found

    if missing:
        raise ValueError(
            "unknown benchmark scenario(s): "
            + ", ".join(sorted(missing))
        )

    return selected


def make_client(
    args: argparse.Namespace,
    *,
    confirmations: int,
) -> BlockchainClient:
    """Create a blockchain client for one scenario."""

    settings = BlockchainClientSettings(
        provider_uri=args.rpc_url,
        chain_id=args.chain_id,
        contract_address=args.contract_address,
        artifact_path=args.artifact_path,
        confirmation_blocks=confirmations,
        signer_private_key=args.writer_private_key,
        proof_of_authority=True,
    )

    return BlockchainClient(settings)


def run_plan(
    plan: BenchmarkScenarioPlan,
    args: argparse.Namespace,
) -> list[Path]:
    """Run one scenario for all configured repetitions."""

    exported_paths: list[Path] = []

    for repetition in range(
        1,
        plan.repetitions + 1,
    ):
        client = make_client(
            args,
            confirmations=plan.scenario.confirmations,
        )

        client.validate_connection()

        observer = PrometheusObserver(
            args.prometheus_url
        )

        before = observer.capture()
        observer.validate_snapshot(before)

        runner = BenchmarkRunner(client)

        result = runner.run(
            plan.scenario,
            repetition=repetition,
        )

        after = observer.capture()

        observer.validate_snapshot(after)

        summary = summarize_run(result)

        paths = export_run_bundle(
            result,
            summary,
            args.output_directory,
        )

        network_path = write_network_observation(
            BenchmarkNetworkObservation(
                run_id=result.run_id,
                prometheus_url=args.prometheus_url,
                before=before,
                after=after,
            ),
            args.output_directory,
        )

        exported_paths.extend(
            [
                paths.run_json,
                paths.transactions_csv,
                paths.summary_json,
                network_path,
            ]
        )

        print(
            "scenario="
            f"{plan.scenario.name} "
            f"repetition={repetition} "
            f"submitted={summary.submitted} "
            f"successful={summary.successful} "
            f"failed={summary.failed} "
            f"throughput_tps={summary.throughput_tps:.4f} "
            f"p95_seconds="
            f"{_format_optional_float(summary.latency_p95_seconds)}"
        )

    return exported_paths


def _format_optional_float(
    value: float | None,
) -> str:
    if value is None:
        return "n/a"

    return f"{value:.4f}"


def execute(
    args: argparse.Namespace,
) -> list[Path]:
    """Load configuration and execute selected benchmark plans."""

    require_configuration(args)

    plans = load_scenario_plans(
        args.scenario_file
    )

    selected = select_plans(
        plans,
        args.scenario_names,
    )

    exported_paths: list[Path] = []

    for plan in selected:
        exported_paths.extend(
            run_plan(
                plan,
                args,
            )
        )

    return exported_paths


def main(
    argv: list[str] | None = None,
) -> int:
    """CLI entry point."""

    parser = build_parser()

    try:
        args = parser.parse_args(argv)

        exported_paths = execute(args)

    except (
        BlockchainClientError,
        OSError,
        ValueError,
    ) as exc:
        print(
            f"benchmark failed: {exc}",
            file=sys.stderr,
        )

        return 1

    print(
        f"benchmark completed: "
        f"{len(exported_paths)} output file(s)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())