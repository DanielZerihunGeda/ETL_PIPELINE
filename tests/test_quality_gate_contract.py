from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_quality_gate_fails_pipeline_and_documents_alert_placeholder() -> None:
    dag_source = (ROOT / "dags/my_python_dag.py").read_text()
    staging_schema = (ROOT / "models/staging/schema.yml").read_text()
    mart_schema = (ROOT / "models/marts/schema.yml").read_text()
    docs = (ROOT / "docs/alerts.md").read_text()

    assert "def notify_failure" in dag_source
    assert "on_failure_callback" in dag_source
    assert "--store-failures" in dag_source
    assert "severity: error" in staging_schema
    assert "severity: error" in mart_schema
    assert "PIPELINE_ALERT_WEBHOOK_URL" in docs
    assert "log-only" in docs
