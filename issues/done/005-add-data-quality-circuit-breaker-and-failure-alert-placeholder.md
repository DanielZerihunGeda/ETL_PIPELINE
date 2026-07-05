# Add Data Quality Circuit Breaker and Failure Alert Placeholder

## Type
AFK

## Blocked by
`004-orchestrate-ingestion-and-dbt-runs-with-airflow.md`

## User stories covered
- User Story 7 - Validate Data Quality
- User Story 11 - Alert on Pipeline Failure

## Goal
Prevent bad data from silently reaching reporting outputs by treating critical dbt test failures as pipeline failures and surfacing a visible failure notification placeholder.

## Implementation notes
- Mark critical dbt tests so failures stop the Airflow pipeline before reporting outputs are treated as refreshed.
- Add or prepare integration points for stronger quality monitoring such as dbt-expectations, Great Expectations, or re-data where practical.
- Ensure Airflow logs clearly show which dbt tests failed and why.
- Add a notification placeholder for pipeline failures, such as email configuration, Slack webhook placeholder, or log-only fallback.
- Document the default alert behavior and how to replace the placeholder with a real notification target.

## Acceptance criteria
- Critical dbt test failures cause the Airflow DAG run to fail.
- Failed tests prevent reporting refresh/promotion behavior from being considered successful.
- Failure details are visible in Airflow task logs.
- A notification placeholder exists and is documented.
- The default implementation does not require a real external alert provider to run locally.

## Verification steps
- Introduce or simulate a failing critical dbt test.
- Trigger the Airflow DAG and confirm the dbt test task fails.
- Confirm downstream reporting-success behavior does not run after the failure.
- Inspect Airflow logs and confirm the failing test details are visible.
- Confirm the alert placeholder behavior is visible or documented.
