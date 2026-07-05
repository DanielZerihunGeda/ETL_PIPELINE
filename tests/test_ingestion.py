import sqlite3

from etl_pipeline.ingestion import IngestionConfig, load_trajectory_files


def test_loads_local_trajectory_file_and_records_metadata(tmp_path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "trajectory.csv").write_text(
        "\n".join(
            [
                "track_id;type;traveled_d;avg_speed;lat;lon;speed;lon_acc;lat_acc;time",
                "1;car;12.5;35.0;9.01;38.76;34.5;0.1;0.2;2026-01-01T00:00:00",
                "2;truck;18.0;28.2;9.02;38.77;29.1;0.1;0.2;2026-01-01T00:00:01",
            ]
        )
    )
    connection = sqlite3.connect(":memory:")

    first = load_trajectory_files(
        connection,
        IngestionConfig(
            data_path=data_dir,
            file_pattern="*.csv",
            dataset_date="2026-01-01",
            area="bole",
            run_identifier="run-001",
        ),
    )
    second = load_trajectory_files(
        connection,
        IngestionConfig(
            data_path=data_dir,
            file_pattern="*.csv",
            dataset_date="2026-01-01",
            area="bole",
            run_identifier="run-001",
        ),
    )

    assert first.total_rows == 2
    assert second.total_rows == 0
    assert second.files[0].status == "skipped"
    assert connection.execute("select count(*) from raw_trajectory_records").fetchone() == (2,)
    assert connection.execute(
        "select source_file, row_count, dataset_date, area, run_identifier "
        "from raw_load_metadata"
    ).fetchall() == [("trajectory.csv", 2, "2026-01-01", "bole", "run-001")]
