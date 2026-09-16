"""Tests for the Phase 2.5C benchmark CLI."""

import importlib.util
from argparse import Namespace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from blockchain_client.benchmark_models import BenchmarkScenario
from blockchain_client.benchmark_scenarios import BenchmarkScenarioPlan

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "network"
    / "besu"
    / "scripts"
    / "benchmark-transactions.py"
)


def load_script() -> ModuleType:
    """Load the benchmark CLI script as a testable module."""

    specification = (
        importlib.util.spec_from_file_location(
            "benchmark_transactions_script",
            SCRIPT_PATH,
        )
    )

    assert specification is not None
    assert specification.loader is not None

    module = importlib.util.module_from_spec(
        specification
    )

    specification.loader.exec_module(module)

    return module


def make_plan(
    name: str = "evidence-c1",
) -> BenchmarkScenarioPlan:
    """Create a benchmark plan for CLI tests."""

    return BenchmarkScenarioPlan(
        scenario=BenchmarkScenario(
            name=name,
            operation="recordEvidence",
            transaction_count=5,
            concurrency=1,
            confirmations=1,
        ),
        repetitions=1,
    )


def make_args(
    tmp_path: Path,
) -> Namespace:
    """Create complete synthetic CLI arguments."""

    return Namespace(
        rpc_url="http://127.0.0.1:8545",
        chain_id=20260720,
        contract_address=(
            "0x"
            + "12" * 20
        ),
        writer_private_key="secret",
        scenario_file=(
            tmp_path / "scenarios.json"
        ),
        scenario_names=None,
        output_directory=tmp_path,
        artifact_path=(
            tmp_path / "artifact.json"
        ),
        prometheus_url=(
            "http://127.0.0.1:9090"
        ),
        allowed_down_instances=[],
        prometheus_step_seconds=15,
    )


def test_select_plans_returns_all_when_no_names() -> None:
    module = load_script()

    plans = (
        make_plan("evidence-c1"),
        make_plan("evidence-c2"),
    )

    selected = module.select_plans(
        plans,
        None,
    )

    assert selected == plans


def test_select_plans_filters_requested_names() -> None:
    module = load_script()

    plans = (
        make_plan("evidence-c1"),
        make_plan("evidence-c2"),
    )

    selected = module.select_plans(
        plans,
        ["evidence-c2"],
    )

    assert len(selected) == 1

    assert (
        selected[0].scenario.name
        == "evidence-c2"
    )


def test_select_plans_supports_multiple_names() -> None:
    module = load_script()

    plans = (
        make_plan("evidence-c1"),
        make_plan("evidence-c2"),
        make_plan("evidence-c5"),
    )

    selected = module.select_plans(
        plans,
        [
            "evidence-c1",
            "evidence-c5",
        ],
    )

    assert [
        plan.scenario.name
        for plan in selected
    ] == [
        "evidence-c1",
        "evidence-c5",
    ]


def test_select_plans_rejects_unknown_name() -> None:
    module = load_script()

    with pytest.raises(
        ValueError,
        match="unknown benchmark scenario",
    ):
        module.select_plans(
            (make_plan(),),
            ["missing"],
        )


@pytest.mark.parametrize(
    (
        "rpc_url",
        "chain_id",
        "contract_address",
        "writer_private_key",
    ),
    [
        (
            None,
            20260720,
            "0x" + "12" * 20,
            "secret",
        ),
        (
            "http://127.0.0.1:8545",
            None,
            "0x" + "12" * 20,
            "secret",
        ),
        (
            "http://127.0.0.1:8545",
            20260720,
            None,
            "secret",
        ),
        (
            "http://127.0.0.1:8545",
            20260720,
            "0x" + "12" * 20,
            None,
        ),
    ],
)
def test_require_configuration_rejects_missing_values(
    rpc_url: str | None,
    chain_id: int | None,
    contract_address: str | None,
    writer_private_key: str | None,
) -> None:
    module = load_script()

    args = Namespace(
        rpc_url=rpc_url,
        chain_id=chain_id,
        contract_address=contract_address,
        writer_private_key=writer_private_key,
    )

    with pytest.raises(
        ValueError,
        match="missing required configuration",
    ):
        module.require_configuration(args)


def test_main_returns_one_on_invalid_configuration(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = load_script()

    monkeypatch.delenv(
        "RPC_URL",
        raising=False,
    )

    monkeypatch.delenv(
        "CHAIN_ID",
        raising=False,
    )

    monkeypatch.delenv(
        "CONTRACT_ADDRESS",
        raising=False,
    )

    monkeypatch.delenv(
        "WRITER_PRIVATE_KEY",
        raising=False,
    )

    result = module.main([])

    captured = capsys.readouterr()

    assert result == 1

    assert (
        "benchmark failed:"
        in captured.err
    )


def test_parser_accepts_allowed_down_instance() -> None:
    module = load_script()
    args = module.build_parser().parse_args(
        ["--allowed-down-instance", "validator-4:9545"]
    )

    assert args.allowed_down_instances == ["validator-4:9545"]
    metadata = module.build_experiment_metadata(
        tuple(args.allowed_down_instances)
    )
    assert metadata.experiment_condition == "3/4_validators_active"
    assert metadata.active_validators == 3


def test_experiment_metadata_rejects_rpc_as_allowed_down() -> None:
    module = load_script()

    with pytest.raises(ValueError, match="known validator"):
        module.build_experiment_metadata(("rpc-node:9545",))


def test_execute_runs_selected_plans(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = load_script()

    calls: list[str] = []

    plans = (
        make_plan("evidence-c1"),
        make_plan("evidence-c2"),
    )

    monkeypatch.setattr(
        module,
        "load_scenario_plans",
        lambda path: plans,
    )

    def fake_run_plan(
        plan: BenchmarkScenarioPlan,
        args: Namespace,
    ) -> list[Path]:
        del args

        calls.append(
            plan.scenario.name
        )

        return [
            tmp_path
            / f"{plan.scenario.name}.json"
        ]

    monkeypatch.setattr(
        module,
        "run_plan",
        fake_run_plan,
    )

    args = make_args(
        tmp_path
    )

    args.scenario_names = [
        "evidence-c2"
    ]

    outputs = module.execute(args)

    assert calls == [
        "evidence-c2"
    ]

    assert len(outputs) == 1


def test_run_plan_captures_network_before_and_after(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = load_script()

    events: list[str] = []

    before_snapshot = object()
    after_snapshot = object()
    time_series = (object(),)
    started_at = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)

    class FakeClient:
        def validate_connection(
            self,
        ) -> None:
            events.append(
                "blockchain-validated"
            )

    class FakeObserver:
        def __init__(
            self,
            base_url: str,
        ) -> None:
            assert (
                base_url
                == "http://127.0.0.1:9090"
            )

            self.capture_count = 0

        def capture(
            self,
        ) -> object:
            self.capture_count += 1

            if self.capture_count == 1:
                events.append(
                    "capture-before"
                )

                return before_snapshot

            events.append(
                "capture-after"
            )

            return after_snapshot

        def validate_snapshot(
            self,
            snapshot: object,
            **kwargs: object,
        ) -> None:
            assert kwargs["expected_instances"] == module.EXPECTED_BESU_INSTANCES
            assert kwargs["allowed_down_instances"] == ()
            if snapshot is before_snapshot:
                events.append(
                    "validate-before"
                )
            elif snapshot is after_snapshot:
                events.append(
                    "validate-after"
                )
            else:
                raise AssertionError(
                    "unexpected snapshot"
                )

        def capture_range(
            self,
            start: datetime,
            end: datetime,
            *,
            step_seconds: int,
        ) -> tuple[object, ...]:
            assert start == started_at
            assert end == started_at + timedelta(seconds=30)
            assert step_seconds == 15
            events.append("capture-range")
            return time_series

    class FakeRunner:
        def __init__(
            self,
            client: Any,
        ) -> None:
            assert isinstance(
                client,
                FakeClient,
            )

        def run(
            self,
            scenario: BenchmarkScenario,
            *,
            repetition: int,
        ) -> Any:
            assert (
                scenario.name
                == "evidence-c1"
            )

            assert repetition == 1

            events.append(
                "benchmark-run"
            )

            return SimpleNamespace(
                run_id="run-001",
                started_at=started_at,
                finished_at=started_at + timedelta(seconds=30),
            )

    summary = SimpleNamespace(
        submitted=5,
        successful=5,
        failed=0,
        throughput_tps=1.25,
        latency_p95_seconds=4.5,
    )

    application_paths = (
        SimpleNamespace(
            run_json=(
                tmp_path
                / "run-run-001.json"
            ),
            transactions_csv=(
                tmp_path
                / "transactions-run-001.csv"
            ),
            summary_json=(
                tmp_path
                / "summary-run-001.json"
            ),
        )
    )

    captured_observation: list[Any] = []

    monkeypatch.setattr(
        module,
        "make_client",
        lambda args, confirmations: FakeClient(),
    )

    monkeypatch.setattr(
        module,
        "PrometheusObserver",
        FakeObserver,
    )

    monkeypatch.setattr(
        module,
        "BenchmarkRunner",
        FakeRunner,
    )

    monkeypatch.setattr(
        module,
        "summarize_run",
        lambda result: summary,
    )

    monkeypatch.setattr(
        module,
        "export_run_bundle",
        lambda result, summary_value, directory, experiment: application_paths,
    )

    def fake_write_network_observation(
        observation: Any,
        directory: Path,
    ) -> Path:
        assert directory == tmp_path

        captured_observation.append(
            observation
        )

        events.append(
            "network-export"
        )

        return (
            tmp_path
            / "network-run-001.json"
        )

    monkeypatch.setattr(
        module,
        "write_network_observation",
        fake_write_network_observation,
    )

    def fake_write_prometheus_timeseries(
        run_id: str,
        samples: tuple[object, ...],
        directory: Path,
    ) -> Path:
        assert run_id == "run-001"
        assert samples is time_series
        assert directory == tmp_path
        events.append("timeseries-export")
        return tmp_path / "metrics-timeseries-run-001.csv"

    monkeypatch.setattr(
        module,
        "write_prometheus_timeseries",
        fake_write_prometheus_timeseries,
    )

    paths = module.run_plan(
        make_plan(),
        make_args(tmp_path),
    )

    assert events == [
        "blockchain-validated",
        "capture-before",
        "validate-before",
        "benchmark-run",
        "capture-after",
        "validate-after",
        "capture-range",
        "network-export",
        "timeseries-export",
    ]

    assert len(paths) == 5

    assert paths == [
        tmp_path / "run-run-001.json",
        tmp_path
        / "transactions-run-001.csv",
        tmp_path
        / "summary-run-001.json",
        tmp_path
        / "network-run-001.json",
        tmp_path
        / "metrics-timeseries-run-001.csv",
    ]

    assert (
        len(captured_observation)
        == 1
    )

    observation = (
        captured_observation[0]
    )

    assert observation.run_id == (
        "run-001"
    )

    assert (
        observation.prometheus_url
        == "http://127.0.0.1:9090"
    )

    assert (
        observation.before
        is before_snapshot
    )

    assert (
        observation.after
        is after_snapshot
    )
    assert observation.experiment.experiment_condition == "4/4_validators_active"
