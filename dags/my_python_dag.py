from __future__ import annotations

import logging
import os
import urllib.request
from datetime import datetime
from typing import Any

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from etl_pipeline.ingestion import run_from_env


logger = logging.getLogger(__name__)


def _runtime_value(context: dict[str, Any], key: str, env_name: str) -> str | None:
    dag_run = context.get("dag_run")
    if dag_run and dag_run.conf and key in dag_run.conf:
        return str(dag_run.conf[key])
    params = context.get("params", {})
    if key in params and params[key] not in {None, ""}:
        return str(params[key])
    return os.environ.get(env_name)


def _apply_runtime_config(**context: Any) -> dict[str, str | None]:
    resolved = {
        "TRAJECTORY_DATA_PATH": _runtime_value(
            context, "trajectory_data_path", "TRAJECTORY_DATA_PATH"
        ),
        "TRAJECTORY_FILE_PATTERN": _runtime_value(
            context, "trajectory_file_pattern", "TRAJECTORY_FILE_PATTERN"
        ),
        "TRAJECTORY_DELIMITER": _runtime_value(
            context, "trajectory_delimiter", "TRAJECTORY_DELIMITER"
        ),
        "DATASET_DATE": _runtime_value(context, "dataset_date", "DATASET_DATE"),
        "DATASET_AREA": _runtime_value(context, "dataset_area", "DATASET_AREA"),
        "RUN_IDENTIFIER": _runtime_value(context, "run_identifier", "RUN_IDENTIFIER")
        or context["run_id"],
    }
    for env_name, value in resolved.items():
        if value is not None:
            os.environ[env_name] = value
    return resolved


def log_config(**context: Any) -> None:
    resolved = _apply_runtime_config(**context)
    logger.info("Trajectory pipeline runtime config: %s", resolved)


def ingest_files(**context: Any) -> None:
    resolved = _apply_runtime_config(**context)
    logger.info("Starting trajectory ingestion with config: %s", resolved)
    summary = run_from_env()
    logger.info("Trajectory ingestion summary: %s", summary)


def notify_failure(context: dict[str, Any]) -> None:
    task_instance = context.get("task_instance")
    dag_run = context.get("dag_run")
    message = (
        "Pipeline failure placeholder: "
        f"dag_id={getattr(dag_run, 'dag_id', None)} "
        f"run_id={getattr(dag_run, 'run_id', None)} "
        f"task_id={getattr(task_instance, 'task_id', None)} "
        f"log_url={getattr(task_instance, 'log_url', None)}"
    )
    webhook_url = os.environ.get("PIPELINE_ALERT_WEBHOOK_URL")
    if not webhook_url:
        logger.error("%s; PIPELINE_ALERT_WEBHOOK_URL is not set, using log-only alert", message)
        return

    request = urllib.request.Request(
        webhook_url,
        data=message.encode("utf-8"),
        method="POST",
        headers={"Content-Type": "text/plain"},
    )
    try:
        urllib.request.urlopen(request, timeout=10).close()
    except Exception:
        logger.exception("Failed sending pipeline failure placeholder alert")
        logger.error(message)


DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": notify_failure,
}


with DAG(
    dag_id="vehicle_trajectory_pipeline",
    description="Load local trajectory files, run dbt models, and execute dbt tests.",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "trajectory_data_path": os.environ.get("TRAJECTORY_DATA_PATH", "/opt/airflow/data"),
        "trajectory_file_pattern": os.environ.get("TRAJECTORY_FILE_PATTERN", "*.csv"),
        "trajectory_delimiter": os.environ.get("TRAJECTORY_DELIMITER", ";"),
        "dataset_date": os.environ.get("DATASET_DATE"),
        "dataset_area": os.environ.get("DATASET_AREA"),
        "run_identifier": os.environ.get("RUN_IDENTIFIER", "manual"),
    },
    tags=["traffic", "trajectory", "dbt"],
) as dag:
    log_runtime_config = PythonOperator(
        task_id="log_runtime_config",
        python_callable=log_config,
    )

    ingest_trajectory_files = PythonOperator(
        task_id="ingest_trajectory_files",
        python_callable=ingest_files,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            "cd ${DBT_PROJECT_DIR:-/opt/airflow/dbt} && "
            "dbt run --profiles-dir ${DBT_PROFILES_DIR:-/opt/airflow/.dbt} "
            "--target ${DBT_TARGET:-dev}"
        ),
        append_env=True,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            "cd ${DBT_PROJECT_DIR:-/opt/airflow/dbt} && "
            "dbt test --profiles-dir ${DBT_PROFILES_DIR:-/opt/airflow/.dbt} "
            "--target ${DBT_TARGET:-dev} --store-failures"
        ),
        append_env=True,
    )

    log_runtime_config >> ingest_trajectory_files >> dbt_run >> dbt_test
