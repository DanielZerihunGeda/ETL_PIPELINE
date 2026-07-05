# Redash Dashboard Setup

Open Redash at http://localhost:5000 after the Docker stack is running.

Create a PostgreSQL data source named `Local Traffic Warehouse` with these local settings:

- Host: `warehouse-postgres`
- Port: `5432`
- Database: `traffic_warehouse`
- User: `warehouse`
- Password: value of `WAREHOUSE_PASSWORD` from `.env`

The default dashboard definition is stored in `redash/assets/traffic_overview_dashboard.json`. It contains queries over:

- `mart.fct_trajectory_runs`
- `mart.vehicle_type_metrics`

Default metric choices are intentionally simple placeholders: row counts by dataset/run, vehicle counts by type, average track speed, average observed speed, and observed time coverage. Refine these once exact traffic business metrics are supplied.

To recreate the dashboard manually, create the listed queries in Redash, add their visualizations, and place them on a dashboard named `Traffic Trajectory Overview`.

## Export Versioned Assets

After the dashboard exists in Redash, export API-backed dashboard and query definitions with:

```bash
REDASH_URL=http://localhost:5000 \
REDASH_API_KEY=<your-api-key> \
REDASH_DASHBOARD_IDS=<dashboard-id> \
REDASH_EXPORT_DIR=redash/exports \
uv run python -m etl_pipeline.redash_export
```

Required environment variables:

- `REDASH_URL`: Redash base URL, for example `http://localhost:5000`
- `REDASH_API_KEY`: user API key from Redash; it is never written to exported files
- `REDASH_DASHBOARD_IDS`: comma-separated dashboard ids to export
- `REDASH_EXPORT_DIR`: output folder, defaulting to `redash/exports`

The exporter writes stable JSON into `dashboards/`, `queries/`, and `manifest.json`.
