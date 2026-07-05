# Bootstrap Dockerized Warehouse Stack

## Type
AFK

## Blocked by
None

## User stories covered
- User Story 1 - Start the Local Stack
- User Story 2 - Configure Warehouse Environments

## Goal
Create the local Docker Compose foundation for the warehouse stack so PostgreSQL, Airflow, Redash, and a dbt-capable execution environment can run together from one command.

## Implementation notes
- Add a Docker Compose setup for PostgreSQL, Airflow, Redash, and required supporting services.
- Persist PostgreSQL data, Airflow metadata, and Redash metadata with Docker volumes.
- Add environment-driven configuration for service ports, database credentials, warehouse database name, and local data path mounts.
- Add PostgreSQL initialization SQL or migrations that create raw, staging, and production-ready mart schemas.
- Include health checks or startup dependencies where practical so dependent services wait for PostgreSQL and metadata stores.
- Keep source data as a local placeholder path; do not download external data at runtime.

## Acceptance criteria
- `docker compose up` starts the local PostgreSQL, Airflow, Redash, and dbt-capable services.
- PostgreSQL contains separate raw, staging, and production-ready schemas.
- Credentials, ports, database names, and local data mounts are configurable through environment variables.
- PostgreSQL, Airflow, and Redash metadata persist across container restarts.
- The stack can be started without requiring cloud services or external source data downloads.

## Verification steps
- Run `docker compose config` and confirm the Compose file resolves successfully.
- Run `docker compose up` and confirm the core services become healthy or reachable.
- Connect to PostgreSQL and confirm the raw, staging, and mart schemas exist.
- Restart the stack and confirm persisted metadata/data is retained.
