from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DASHBOARD_PATH = Path(
    "network/besu/monitoring/grafana/provisioning/dashboards/besu-qbft-overview.json"
)
CONFIRMED_METRICS = {
    "besu_blockchain_chain_head_transaction_count",
    "besu_executors_bfttimerexecutor_qbft_active_threads_current",
    "besu_rpc_active_http_connection_count",
    "besu_synchronizer_in_sync",
    "besu_transaction_pool_number_of_transactions",
    "ethereum_blockchain_height",
    "ethereum_peer_count",
    "jvm_gc_collection_seconds_count",
    "jvm_gc_collection_seconds_sum",
    "jvm_memory_used_bytes",
    "jvm_threads_current",
    "process_cpu_seconds_total",
    "process_open_fds",
    "process_resident_memory_bytes",
    "up",
}


def load_dashboard() -> dict[str, Any]:
    result: dict[str, Any] = json.loads(DASHBOARD_PATH.read_text(encoding="utf-8"))
    return result


def query_panels(dashboard: dict[str, Any]) -> list[dict[str, Any]]:
    return [panel for panel in dashboard["panels"] if panel.get("targets")]


def test_dashboard_identity_and_panel_ids() -> None:
    dashboard = load_dashboard()
    panels = dashboard["panels"]
    panel_ids = [panel["id"] for panel in panels]

    assert dashboard["title"] == "Besu QBFT Private Network Overview"
    assert dashboard["uid"] == "besu-qbft-overview"
    assert len(panel_ids) == len(set(panel_ids))
    assert all(panel.get("title") for panel in panels)
    assert all(panel.get("description") for panel in panels)


def test_dashboard_uses_prometheus_datasource_and_nonempty_queries() -> None:
    dashboard = load_dashboard()

    for panel in query_panels(dashboard):
        assert panel["datasource"] == {"type": "prometheus", "uid": "prometheus"}
        assert all(target.get("expr", "").strip() for target in panel["targets"])

    variable = dashboard["templating"]["list"][0]
    assert variable["datasource"] == {"type": "prometheus", "uid": "prometheus"}


def test_promql_only_references_confirmed_metrics() -> None:
    dashboard = load_dashboard()
    expressions = [
        target["expr"] for panel in query_panels(dashboard) for target in panel["targets"]
    ]
    referenced = {
        match.group(1)
        for expression in expressions
        for match in re.finditer(r"\b([a-zA-Z_:][a-zA-Z0-9_:]*)\s*\{", expression)
    }

    assert referenced
    assert referenced <= CONFIRMED_METRICS


def test_dashboard_has_expected_data_panels_and_no_evidence_totals() -> None:
    dashboard = load_dashboard()
    data_panels = query_panels(dashboard)
    titles = {panel["title"] for panel in dashboard["panels"]}

    assert len(data_panels) == 26
    assert "Total Evidence" not in titles
    assert "Total Access" not in titles
