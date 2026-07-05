# dbt Lineage Screenshot Placeholder

Generate docs with:

```bash
docker compose run --rm dbt dbt docs generate
docker compose run --rm -p 8081:8080 dbt dbt docs serve --host 0.0.0.0 --port 8080
```

Capture the lineage view showing:

- `raw.trajectory_records`
- `stg_trajectory_records`
- `fct_trajectory_runs`
- `vehicle_type_metrics`
