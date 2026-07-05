from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_dbt_project_declares_raw_sources_staging_and_marts() -> None:
    source_yaml = (ROOT / "models/sources.yml").read_text()
    staging_sql = (ROOT / "models/staging/stg_trajectory_records.sql").read_text()
    mart_sql = (ROOT / "models/marts/fct_trajectory_runs.sql").read_text()
    project_yaml = (ROOT / "dbt_project.yml").read_text()
    schema_macro = (ROOT / "macros/generate_schema_name.sql").read_text()

    assert "schema: raw" in source_yaml
    assert "name: trajectory_records" in source_yaml
    assert "name: load_metadata" in source_yaml
    assert "source('raw', 'trajectory_records')" in staging_sql
    assert "raw_payload" in staging_sql
    assert "ref('stg_trajectory_records')" in mart_sql
    assert "staging:" in project_yaml
    assert "+schema: staging" in project_yaml
    assert "marts:" in project_yaml
    assert "+schema: mart" in project_yaml
    assert "custom_schema_name" in schema_macro
