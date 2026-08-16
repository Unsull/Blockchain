"""Load and validate benchmark scenario configuration."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from blockchain_client.benchmark_models import (
    BenchmarkOperation,
    BenchmarkScenario,
)


@dataclass(frozen=True)
class BenchmarkScenarioPlan:
    """One benchmark scenario and its repetition count."""

    scenario: BenchmarkScenario
    repetitions: int

    def validate(self) -> None:
        """Validate the complete benchmark plan entry."""

        self.scenario.validate()

        if self.repetitions <= 0:
            raise ValueError("repetitions must be positive")


def load_scenario_plans(
    path: Path,
) -> tuple[BenchmarkScenarioPlan, ...]:
    """Load benchmark scenarios from a JSON configuration file."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(
            f"failed to read benchmark scenario file: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid benchmark scenario JSON: {path}"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError("benchmark configuration must be a JSON object")

    unknown_top_level = set(payload) - {"scenarios"}

    if unknown_top_level:
        raise ValueError(
            "unknown benchmark configuration field(s): "
            + ", ".join(sorted(unknown_top_level))
        )

    raw_scenarios = payload.get("scenarios")

    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        raise ValueError("scenarios must be a non-empty list")

    plans = tuple(
        _parse_scenario(
            raw_scenario,
            index=index,
        )
        for index, raw_scenario in enumerate(
            raw_scenarios,
            start=1,
        )
    )

    names = [
        plan.scenario.name
        for plan in plans
    ]

    if len(names) != len(set(names)):
        raise ValueError("benchmark scenario names must be unique")

    return plans


def _parse_scenario(
    raw_scenario: Any,
    *,
    index: int,
) -> BenchmarkScenarioPlan:
    if not isinstance(raw_scenario, dict):
        raise ValueError(
            f"scenario {index} must be a JSON object"
        )

    required_fields = {
        "name",
        "operation",
        "transaction_count",
        "concurrency",
        "confirmations",
        "repetitions",
    }

    actual_fields = set(raw_scenario)

    missing_fields = required_fields - actual_fields
    unknown_fields = actual_fields - required_fields

    if missing_fields:
        raise ValueError(
            f"scenario {index} missing field(s): "
            + ", ".join(sorted(missing_fields))
        )

    if unknown_fields:
        raise ValueError(
            f"scenario {index} unknown field(s): "
            + ", ".join(sorted(unknown_fields))
        )

    name = raw_scenario["name"]

    if not isinstance(name, str):
        raise ValueError(
            f"scenario {index} name must be a string"
        )

    raw_operation = raw_scenario["operation"]

    if raw_operation not in (
        "recordEvidence",
        "recordAccess",
    ):
        raise ValueError(
            f"scenario {index} has unsupported operation"
        )

    operation = cast(
        BenchmarkOperation,
        raw_operation,
    )

    scenario = BenchmarkScenario(
        name=name,
        operation=operation,
        transaction_count=_require_int(
            raw_scenario["transaction_count"],
            field="transaction_count",
            index=index,
        ),
        concurrency=_require_int(
            raw_scenario["concurrency"],
            field="concurrency",
            index=index,
        ),
        confirmations=_require_int(
            raw_scenario["confirmations"],
            field="confirmations",
            index=index,
        ),
    )

    plan = BenchmarkScenarioPlan(
        scenario=scenario,
        repetitions=_require_int(
            raw_scenario["repetitions"],
            field="repetitions",
            index=index,
        ),
    )

    plan.validate()

    return plan


def _require_int(
    value: Any,
    *,
    field: str,
    index: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"scenario {index} {field} must be an integer"
        )

    return cast(int, value)