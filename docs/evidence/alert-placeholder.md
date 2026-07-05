# Alert Placeholder Evidence

The default alert mode is log-only. To capture evidence, trigger a failing dbt test and inspect the Airflow task logs for:

- Failed DAG id
- Failed run id
- Failed task id
- Airflow task log URL

Set `PIPELINE_ALERT_WEBHOOK_URL` to replace this placeholder with a real webhook target.
