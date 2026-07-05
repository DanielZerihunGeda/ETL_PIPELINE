# Traffic Trajectory ETL Pipeline

This project builds a local traffic trajectory warehouse with PostgreSQL, Airflow, dbt, and Redash. It loads local trajectory CSV files into raw tables, transforms them through staging and mart models, runs dbt quality checks, and exposes default Redash dashboard assets.

## Quick Start

```bash
cp .env.example .env
docker compose config
docker compose up --build
```

The stack is local-only. It does not download source trajectory data at runtime; mount or copy your own files into the configured local data path.

## Service URLs

- Airflow: http://localhost:8080
- Redash: http://localhost:5000
- PostgreSQL warehouse: `localhost:5432`

Default development credentials live in `.env.example`. Change them in `.env` for any shared environment.

## Environment Variables

Core stack variables:

- `WAREHOUSE_DB`, `WAREHOUSE_USER`, `WAREHOUSE_PASSWORD`, `WAREHOUSE_PORT`
- `AIRFLOW_PORT`, `AIRFLOW_ADMIN_USERNAME`, `AIRFLOW_ADMIN_PASSWORD`
- `REDASH_PORT`, `REDASH_URL`, `REDASH_API_KEY`, `REDASH_DASHBOARD_IDS`
- `LOCAL_DATA_PATH`: host path mounted read-only into Airflow/dbt containers

Pipeline variables:

- `TRAJECTORY_DATA_PATH`: container path for input files, default `/opt/airflow/data`
- `TRAJECTORY_FILE_PATTERN`: file glob, default `*.csv`
- `TRAJECTORY_DELIMITER`: CSV delimiter, default `;`
- `DATASET_DATE`, `DATASET_AREA`, `RUN_IDENTIFIER`
- `DBT_PROJECT_DIR`, `DBT_PROFILES_DIR`, `DBT_TARGET`
- `PIPELINE_ALERT_WEBHOOK_URL`: optional failure alert webhook; unset means log-only

## Configure Local Source Data

Place trajectory CSV files under `./data` or set `LOCAL_DATA_PATH` in `.env` to another local folder. The ingestion task preserves each source row in `raw.trajectory_records.raw_payload` and writes file/run audit metadata to `raw.load_metadata`.

Expected default CSV fields include:

- `track_id`
- `type`
- `traveled_d`
- `avg_speed`
- `lat`
- `lon`
- `speed`
- `lon_acc`
- `lat_acc`
- `time`

## Run the Pipeline

Open Airflow and trigger the `vehicle_trajectory_pipeline` DAG. You can override the default runtime config through DAG run config:

```json
{
  "trajectory_data_path": "/opt/airflow/data",
  "trajectory_file_pattern": "*.csv",
  "dataset_date": "2026-01-01",
  "dataset_area": "local",
  "run_identifier": "manual-001"
}
```

The DAG runs:

1. `log_runtime_config`
2. `ingest_trajectory_files`
3. `dbt_run`
4. `dbt_test`

The ingestion step is idempotent for each `source_file` and `run_identifier` pair.

## Warehouse Flow

- `raw`: local file ingestion output and load metadata
- `staging`: typed, audit-preserving dbt staging views
- `mart`: analytics-ready dbt models for Redash

Primary dbt models:

- `stg_trajectory_records`
- `stg_load_metadata`
- `fct_trajectory_runs`
- `vehicle_type_metrics`

## dbt Documentation

Run dbt commands through the dbt-capable container:

```bash
docker compose run --rm dbt dbt debug
docker compose run --rm dbt dbt run
docker compose run --rm dbt dbt test --store-failures
docker compose run --rm dbt dbt docs generate
docker compose run --rm -p 8081:8080 dbt dbt docs serve --host 0.0.0.0 --port 8080
```

Then open dbt docs at http://localhost:8081.

## Redash Dashboard

Open Redash at http://localhost:5000. Create a PostgreSQL data source named `Local Traffic Warehouse`:

- Host: `warehouse-postgres`
- Port: `5432`
- Database: value of `WAREHOUSE_DB`, default `traffic_warehouse`
- User: value of `WAREHOUSE_USER`, default `warehouse`
- Password: value of `WAREHOUSE_PASSWORD`

The default dashboard definition is in `redash/assets/traffic_overview_dashboard.json`. It uses placeholder traffic metrics from `mart.fct_trajectory_runs` and `mart.vehicle_type_metrics`, including row counts, vehicle counts by type, average speed, and observed time coverage.

## Export Redash Assets

After creating a dashboard in Redash, export version-control-friendly definitions:

```bash
REDASH_URL=http://localhost:5000 \
REDASH_API_KEY=<your-api-key> \
REDASH_DASHBOARD_IDS=<dashboard-id> \
REDASH_EXPORT_DIR=redash/exports \
uv run python -m etl_pipeline.redash_export
```

The exporter writes stable JSON under `dashboards/`, `queries/`, and `manifest.json`, and strips secret-like fields before writing files.

## Failure Alerts

Critical dbt tests use `severity: error`. The Airflow `dbt_test` task runs with `--store-failures`; a failed test fails the task and stops the DAG run from being considered successful.

By default, failure notification is log-only. Set `PIPELINE_ALERT_WEBHOOK_URL` to send a plain-text POST placeholder alert to a real webhook later. See `docs/alerts.md`.

## Evidence Placeholders

- Tech-stack flow diagram: `docs/evidence/tech-stack-flow.md`
- dbt lineage screenshot: `docs/evidence/dbt-lineage-screenshot.md`
- Redash dashboard screenshot: `docs/evidence/redash-dashboard-screenshot.md`
- Alert placeholder evidence: `docs/evidence/alert-placeholder.md`
