import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_airflow_dag_orchestrates_ingestion_then_dbt() -> None:
    dag_path = ROOT / "dags/my_python_dag.py"
    dag_source = dag_path.read_text()

    ast.parse(dag_source)

    assert "dag_id=\"vehicle_trajectory_pipeline\"" in dag_source
    assert "task_id=\"log_runtime_config\"" in dag_source
    assert "task_id=\"ingest_trajectory_files\"" in dag_source
    assert "task_id=\"dbt_run\"" in dag_source
    assert "task_id=\"dbt_test\"" in dag_source
    assert "log_runtime_config >> ingest_trajectory_files >> dbt_run >> dbt_test" in dag_source
    assert "run_from_env()" in dag_source
    assert "dbt run" in dag_source
    assert "dbt test" in dag_source
