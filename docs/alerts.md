# Pipeline Failure Alerts

Airflow treats the `dbt_test` task as the data quality circuit breaker. Critical dbt tests are configured with `severity: error`, and the DAG runs `dbt test --store-failures` after `dbt run`. A failing critical test returns a non-zero exit code, fails the Airflow task, and stops the DAG run from being considered successful.

The default alert behavior is log-only. The DAG has an `on_failure_callback` that logs the failed DAG id, run id, task id, and Airflow log URL. This keeps local development free of external alert provider requirements.

To replace the placeholder with a real alert target, set `PIPELINE_ALERT_WEBHOOK_URL` in the Airflow environment. The callback sends a plain-text POST to that URL. Leave it unset for the local log-only fallback.
