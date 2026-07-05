# Build dbt Sources, Staging Models, and Documentation

## Type
AFK

## Blocked by
`002-load-local-trajectory-data-into-raw-postgresql-tables.md`

## User stories covered
- User Story 5 - Transform Raw Data with dbt
- User Story 8 - Generate and Serve dbt Documentation

## Goal
Create a working dbt project that connects to PostgreSQL, declares raw trajectory sources, builds cleaned staging models, builds final analytics-ready models, and produces dbt documentation artifacts.

## Implementation notes
- Configure dbt for PostgreSQL using environment-driven profile values.
- Declare raw trajectory tables and load metadata tables as dbt sources.
- Build staging models that clean and normalize raw trajectory data without losing auditability.
- Build final analytical models suitable for Redash traffic metrics.
- Add model and column descriptions in dbt YAML files.
- Add dbt tests for baseline not-null, accepted values, uniqueness, and relationship checks where the data shape supports them.
- Ensure `dbt docs generate` works locally and produces lineage/documentation artifacts.

## Acceptance criteria
- dbt connects to the local PostgreSQL warehouse.
- Raw PostgreSQL tables are declared as dbt sources.
- dbt builds staging models in the staging schema.
- dbt builds final reporting models in the production-ready mart schema.
- dbt model and column documentation exists for raw sources, staging models, and final models.
- dbt docs can be generated locally.

## Verification steps
- Run `dbt debug` from the dbt execution environment and confirm the connection succeeds.
- Run `dbt run` and confirm staging and final models are created in PostgreSQL.
- Run `dbt test` and confirm baseline tests execute.
- Run `dbt docs generate` and confirm documentation artifacts are created.
