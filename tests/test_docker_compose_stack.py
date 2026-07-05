import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def compose_config(env_file: str = ".env.example") -> dict:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "--env-file",
            env_file,
            "config",
            "--format",
            "json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_compose_config_defines_local_warehouse_stack() -> None:
    config = compose_config()

    assert set(config["services"]) >= {
        "warehouse-postgres",
        "airflow-postgres",
        "airflow-init",
        "airflow-webserver",
        "airflow-scheduler",
        "redis",
        "redash-postgres",
        "redash",
        "redash-worker",
        "dbt",
    }
    assert set(config["volumes"]) >= {
        "warehouse_postgres_data",
        "airflow_postgres_data",
        "airflow_logs",
        "redash_postgres_data",
        "redis_data",
    }


def test_long_running_services_wait_for_datastores() -> None:
    services = compose_config()["services"]

    assert set(services["airflow-webserver"]["depends_on"]) >= {
        "airflow-postgres",
        "warehouse-postgres",
    }
    assert set(services["airflow-scheduler"]["depends_on"]) >= {
        "airflow-postgres",
        "warehouse-postgres",
    }
    assert set(services["redash"]["depends_on"]) >= {"redash-postgres", "redis"}
    assert set(services["redash-worker"]["depends_on"]) >= {"redash-postgres", "redis"}


def test_stack_settings_are_environment_configurable(tmp_path: Path) -> None:
    env_file = tmp_path / "stack.env"
    env_file.write_text(
        "\n".join(
            [
                "COMPOSE_PROJECT_NAME=custom_etl",
                "WAREHOUSE_DB=custom_warehouse",
                "WAREHOUSE_USER=custom_user",
                "WAREHOUSE_PASSWORD=custom_password",
                "WAREHOUSE_PORT=15432",
                f"LOCAL_DATA_PATH={tmp_path}",
                "AIRFLOW_DB_NAME=custom_airflow",
                "AIRFLOW_DB_USER=custom_airflow_user",
                "AIRFLOW_DB_PASSWORD=custom_airflow_password",
                "AIRFLOW_PORT=18080",
                "REDASH_DB_NAME=custom_redash",
                "REDASH_DB_USER=custom_redash_user",
                "REDASH_DB_PASSWORD=custom_redash_password",
                "REDASH_PORT=15000",
            ]
        )
    )

    services = compose_config(str(env_file))["services"]

    assert services["warehouse-postgres"]["environment"] == {
        "POSTGRES_DB": "custom_warehouse",
        "POSTGRES_PASSWORD": "custom_password",
        "POSTGRES_USER": "custom_user",
    }
    assert services["warehouse-postgres"]["ports"][0]["published"] == "15432"
    assert services["airflow-webserver"]["ports"][0]["published"] == "18080"
    assert services["redash"]["ports"][0]["published"] == "15000"
    assert {
        "type": "bind",
        "source": str(tmp_path),
        "target": "/opt/airflow/data",
        "read_only": True,
        "bind": {},
    } in services["dbt"]["volumes"]


def test_warehouse_init_creates_raw_staging_and_mart_schemas() -> None:
    init_sql = (ROOT / "docker/postgres/init/01-create-warehouse-schemas.sql").read_text()

    assert "CREATE SCHEMA IF NOT EXISTS raw;" in init_sql
    assert "CREATE SCHEMA IF NOT EXISTS staging;" in init_sql
    assert "CREATE SCHEMA IF NOT EXISTS mart;" in init_sql
