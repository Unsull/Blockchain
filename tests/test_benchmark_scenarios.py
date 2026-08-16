"""Tests for benchmark scenario configuration."""

import json
from pathlib import Path

import pytest

from blockchain_client.benchmark_scenarios import (
    load_scenario_plans,
)


def write_config(
    path: Path,
    payload: object,
) -> None:
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def test_load_scenario_plans_accepts_valid_configuration(
    tmp_path: Path,
) -> None:
    path = tmp_path / "scenarios.json"

    write_config(
        path,
        {
            "scenarios": [
                {
                    "name": "evidence-c2",
                    "operation": "recordEvidence",
                    "transaction_count": 20,
                    "concurrency": 2,
                    "confirmations": 1,
                    "repetitions": 3,
                },
                {
                    "name": "access-c5",
                    "operation": "recordAccess",
                    "transaction_count": 20,
                    "concurrency": 5,
                    "confirmations": 1,
                    "repetitions": 3,
                },
            ]
        },
    )

    plans = load_scenario_plans(path)

    assert len(plans) == 2
    assert plans[0].scenario.name == "evidence-c2"
    assert plans[0].scenario.concurrency == 2
    assert plans[0].repetitions == 3

    assert plans[1].scenario.operation == "recordAccess"


def test_load_scenario_plans_rejects_duplicate_names(
    tmp_path: Path,
) -> None:
    path = tmp_path / "scenarios.json"

    scenario = {
        "name": "duplicate",
        "operation": "recordEvidence",
        "transaction_count": 5,
        "concurrency": 1,
        "confirmations": 1,
        "repetitions": 1,
    }

    write_config(
        path,
        {
            "scenarios": [
                scenario,
                scenario,
            ]
        },
    )

    with pytest.raises(
        ValueError,
        match="names must be unique",
    ):
        load_scenario_plans(path)


def test_load_scenario_plans_rejects_unknown_operation(
    tmp_path: Path,
) -> None:
    path = tmp_path / "scenarios.json"

    write_config(
        path,
        {
            "scenarios": [
                {
                    "name": "invalid",
                    "operation": "recordDelete",
                    "transaction_count": 5,
                    "concurrency": 1,
                    "confirmations": 1,
                    "repetitions": 1,
                }
            ]
        },
    )

    with pytest.raises(
        ValueError,
        match="unsupported operation",
    ):
        load_scenario_plans(path)


def test_load_scenario_plans_rejects_unknown_field(
    tmp_path: Path,
) -> None:
    path = tmp_path / "scenarios.json"

    write_config(
        path,
        {
            "scenarios": [
                {
                    "name": "invalid",
                    "operation": "recordEvidence",
                    "transaction_count": 5,
                    "concurrency": 1,
                    "confirmations": 1,
                    "repetitions": 1,
                    "concurency": 1,
                }
            ]
        },
    )

    with pytest.raises(
        ValueError,
        match="unknown field",
    ):
        load_scenario_plans(path)