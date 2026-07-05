import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_redash_dashboard_assets_query_transformed_marts() -> None:
    dashboard = json.loads((ROOT / "redash/assets/traffic_overview_dashboard.json").read_text())
    docs = (ROOT / "redash/README.md").read_text()

    query_text = "\n".join(query["query"] for query in dashboard["queries"])

    assert dashboard["dashboard"]["name"] == "Traffic Trajectory Overview"
    assert "mart.fct_trajectory_runs" in query_text
    assert "mart.vehicle_type_metrics" in query_text
    assert "vehicle_count" in query_text
    assert "average_track_speed" in query_text
    assert "http://localhost:5000" in docs
    assert "traffic_warehouse" in docs
