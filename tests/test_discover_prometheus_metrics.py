from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def load_module() -> ModuleType:
    path = Path("network/besu/scripts/discover-prometheus-metrics.py")
    spec = importlib.util.spec_from_file_location("discover_prometheus_metrics", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_filter_metric_names_is_case_insensitive_sorted_and_unique() -> None:
    module = load_module()

    result = module.filter_metric_names(
        ["unrelated", "Ethereum_Blockchain_Height", "besu_peer_count", "besu_peer_count"]
    )

    assert result == ["Ethereum_Blockchain_Height", "besu_peer_count"]


def test_summarize_vector_limits_samples_and_collects_instances() -> None:
    module = load_module()
    result = {
        "data": {
            "resultType": "vector",
            "result": [
                {"metric": {"instance": f"node-{index}", "job": "besu"}, "value": [1, str(index)]}
                for index in range(7)
            ],
        }
    }

    summary = module.summarize_vector(result)

    assert summary["result_type"] == "vector"
    assert len(summary["samples"]) == 5
    assert summary["instances"] == [f"node-{index}" for index in range(5)]


def test_classification_marks_missing_live_metric_unavailable() -> None:
    module = load_module()

    classifications = {
        item["category"]: item for item in module.classify_categories({"up"})
    }

    assert classifications["node availability"]["status"] == "confirmed available"
    assert classifications["block height"]["status"] == "unavailable"
    assert classifications["open file descriptors"]["status"] == "unavailable"
