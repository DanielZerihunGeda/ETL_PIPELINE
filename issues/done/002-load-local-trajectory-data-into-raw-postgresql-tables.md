# Load Local Trajectory Data into Raw PostgreSQL Tables

## Type
AFK

## Blocked by
`001-bootstrap-dockerized-warehouse-stack.md`

## User stories covered
- User Story 3 - Load Local Data Files
- User Story 4 - Parameterize Pipeline Runs

## Goal
Implement a configurable Airflow ingestion path that loads one or more local vehicle trajectory files into raw PostgreSQL tables and records enough metadata to audit each load.

## Implementation notes
- Replace hardcoded file names and database credentials with Airflow Variables, Connections, DAG params, environment variables, or a small config file.
- Support one or more local input files from a configurable mounted data directory.
- Load raw trajectory data without destructive transformation so the original source shape is preserved where practical.
- Record load metadata including source file name, load timestamp, row count, dataset date, area, and run identifier.
- Add an idempotency guard that avoids duplicate inserts for the same file/run combination where practical.
- Log success and failure details clearly from the ingestion task.

## Acceptance criteria
- A local input data path can be changed without editing DAG source code.
- Airflow can load at least one configured local trajectory file into PostgreSQL raw tables.
- The ingestion process records source file name, row count, load timestamp, and run identifier.
- Re-running the same load does not blindly duplicate the same file/run records.
- Ingestion failures are visible in Airflow task logs.

## Verification steps
- Configure a local placeholder data directory and sample trajectory file path.
- Trigger the ingestion DAG or ingestion task from Airflow.
- Query PostgreSQL raw tables and confirm loaded rows exist.
- Query the load metadata table and confirm file/run metadata was recorded.
- Re-run the same input and confirm idempotency behavior is documented and works as implemented.
