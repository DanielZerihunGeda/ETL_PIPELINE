# Build Redash Dashboard from Transformed Models

## Type
AFK

## Blocked by
`005-add-data-quality-circuit-breaker-and-failure-alert-placeholder.md`

## User stories covered
- User Story 9 - Build Redash Dashboard

## Goal
Connect Redash to the transformed PostgreSQL warehouse models and create at least one dashboard with practical default traffic metrics.

## Implementation notes
- Configure Redash so it can connect to the local PostgreSQL warehouse.
- Create default Redash queries over final dbt models, using sensible placeholder traffic metrics until exact business metrics are supplied.
- Include at least one dashboard that visualizes transformed trajectory data.
- Prefer metrics that can be derived from the PRD data shape, such as row counts by dataset/run, vehicle counts by type, average speed, distance traveled, and time-based trajectory coverage.
- Store dashboard setup instructions in the README or a dedicated docs location.
- Do not require external data downloads or cloud services.

## Acceptance criteria
- Redash can connect to the local PostgreSQL warehouse.
- At least one Redash query reads from transformed dbt models.
- At least one Redash dashboard displays traffic-related metrics or visualizations.
- Dashboard setup and access instructions are documented.
- Placeholder/default metric choices are clearly documented for later refinement.

## Verification steps
- Start the local stack and open Redash.
- Configure or confirm the PostgreSQL data source connection.
- Run the dashboard queries and confirm they return rows from transformed models.
- Open the dashboard and confirm at least one visualization renders.
- Confirm the README or docs explain how to access and recreate the dashboard.
