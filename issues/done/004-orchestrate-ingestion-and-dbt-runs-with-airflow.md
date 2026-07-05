# Orchestrate Ingestion and dbt Runs with Airflow

## Type
AFK

## Blocked by
`003-build-dbt-sources-staging-models-and-documentation.md`

## User stories covered
- User Story 3 - Load Local Data Files
- User Story 4 - Parameterize Pipeline Runs
- User Story 6 - Run dbt from Airflow

## Goal
Wire the ingestion and transformation steps into a single Airflow DAG that runs local file loading, dbt transformations, and dbt tests in sequence with reusable runtime configuration.

## Implementation notes
- Refactor the existing prototype DAG into a valid Airflow DAG that can be parsed and scheduled.
- Add tasks for ingestion, `dbt run`, and `dbt test` using BashOperator, PythonOperator, or an equivalent local execution pattern.
- Ensure dbt runs only after successful raw ingestion.
- Ensure dbt tests run after dbt models are built.
- Pass dataset path, dataset date, area, run identifier, schema targets, and load behavior through Airflow Variables, Connections, DAG params, environment variables, or config files.
- Avoid hardcoded database credentials, input paths, and schema names in DAG logic.

## Acceptance criteria
- Airflow can parse the DAG without import or syntax errors.
- Triggering the DAG runs ingestion, `dbt run`, and `dbt test` in order.
- dbt tasks use the configured dbt project/profile paths and target schemas.
- Pipeline configuration can be changed without editing DAG source code.
- Task logs make the current dataset/run configuration visible enough for debugging.

## Verification steps
- Start the local stack and confirm the DAG appears in Airflow.
- Trigger the DAG manually with a configured local input path.
- Confirm task ordering is ingestion, dbt run, then dbt test.
- Confirm PostgreSQL raw, staging, and mart tables are updated by the DAG run.
- Inspect Airflow logs for the resolved run metadata and dbt command output.
