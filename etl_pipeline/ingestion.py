from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IngestionConfig:
    data_path: Path
    file_pattern: str = "*.csv"
    dataset_date: str | None = None
    area: str | None = None
    run_identifier: str = "manual"
    delimiter: str = ";"


@dataclass(frozen=True)
class FileLoadSummary:
    source_file: str
    row_count: int
    status: str


@dataclass(frozen=True)
class LoadSummary:
    files: list[FileLoadSummary]

    @property
    def total_rows(self) -> int:
        return sum(file.row_count for file in self.files if file.status == "loaded")


class RawTrajectoryStore:
    def __init__(self, connection: Any, dialect: str | None = None) -> None:
        self.connection = connection
        self.dialect = dialect or connection.__class__.__module__.split(".", maxsplit=1)[0]
        self.placeholder = "%s" if self.dialect.startswith("psycopg") else "?"

    @property
    def records_table(self) -> str:
        return "raw.trajectory_records" if self.is_postgres else "raw_trajectory_records"

    @property
    def metadata_table(self) -> str:
        return "raw.load_metadata" if self.is_postgres else "raw_load_metadata"

    @property
    def is_postgres(self) -> bool:
        return self.dialect.startswith("psycopg")

    def ensure_tables(self) -> None:
        cursor = self.connection.cursor()
        if self.is_postgres:
            cursor.execute("CREATE SCHEMA IF NOT EXISTS raw")
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw.trajectory_records (
                    id bigserial PRIMARY KEY,
                    source_file text NOT NULL,
                    run_identifier text NOT NULL,
                    dataset_date date,
                    area text,
                    row_number integer NOT NULL,
                    raw_payload jsonb NOT NULL,
                    track_id text,
                    vehicle_type text,
                    traveled_distance numeric,
                    avg_speed numeric,
                    loaded_at timestamptz NOT NULL DEFAULT now(),
                    UNIQUE (source_file, run_identifier, row_number)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw.load_metadata (
                    id bigserial PRIMARY KEY,
                    source_file text NOT NULL,
                    run_identifier text NOT NULL,
                    dataset_date date,
                    area text,
                    row_count integer NOT NULL DEFAULT 0,
                    loaded_at timestamptz NOT NULL DEFAULT now(),
                    UNIQUE (source_file, run_identifier)
                )
                """
            )
        else:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_trajectory_records (
                    id integer PRIMARY KEY AUTOINCREMENT,
                    source_file text NOT NULL,
                    run_identifier text NOT NULL,
                    dataset_date text,
                    area text,
                    row_number integer NOT NULL,
                    raw_payload text NOT NULL,
                    track_id text,
                    vehicle_type text,
                    traveled_distance real,
                    avg_speed real,
                    loaded_at text NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (source_file, run_identifier, row_number)
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS raw_load_metadata (
                    id integer PRIMARY KEY AUTOINCREMENT,
                    source_file text NOT NULL,
                    run_identifier text NOT NULL,
                    dataset_date text,
                    area text,
                    row_count integer NOT NULL DEFAULT 0,
                    loaded_at text NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (source_file, run_identifier)
                )
                """
            )

    def already_loaded(self, source_file: str, run_identifier: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            SELECT 1
            FROM {self.metadata_table}
            WHERE source_file = {self.placeholder}
              AND run_identifier = {self.placeholder}
            LIMIT 1
            """,
            (source_file, run_identifier),
        )
        return cursor.fetchone() is not None

    def insert_records(
        self,
        source_file: str,
        run_identifier: str,
        dataset_date: str | None,
        area: str | None,
        rows: list[dict[str, str]],
    ) -> None:
        cursor = self.connection.cursor()
        statement = f"""
            INSERT INTO {self.records_table} (
                source_file,
                run_identifier,
                dataset_date,
                area,
                row_number,
                raw_payload,
                track_id,
                vehicle_type,
                traveled_distance,
                avg_speed
            )
            VALUES (
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder}
            )
        """
        cursor.executemany(
            statement,
            [
                (
                    source_file,
                    run_identifier,
                    dataset_date,
                    area,
                    index,
                    json.dumps(row, sort_keys=True),
                    row.get("track_id"),
                    row.get("type"),
                    _optional_float(row.get("traveled_d")),
                    _optional_float(row.get("avg_speed")),
                )
                for index, row in enumerate(rows, start=1)
            ],
        )

    def insert_metadata(
        self,
        source_file: str,
        run_identifier: str,
        dataset_date: str | None,
        area: str | None,
        row_count: int,
    ) -> None:
        cursor = self.connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO {self.metadata_table} (
                source_file,
                run_identifier,
                dataset_date,
                area,
                row_count
            )
            VALUES (
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder},
                {self.placeholder}
            )
            """,
            (source_file, run_identifier, dataset_date, area, row_count),
        )


def load_trajectory_files(connection: Any, config: IngestionConfig) -> LoadSummary:
    store = RawTrajectoryStore(connection)
    store.ensure_tables()
    files = sorted(Path(config.data_path).glob(config.file_pattern))
    summaries: list[FileLoadSummary] = []

    if not files:
        raise FileNotFoundError(
            f"No input files matched {config.file_pattern!r} under {config.data_path}"
        )

    for file_path in files:
        source_file = file_path.name
        if store.already_loaded(source_file, config.run_identifier):
            logger.info(
                "Skipping %s for run %s because metadata already exists",
                source_file,
                config.run_identifier,
            )
            summaries.append(FileLoadSummary(source_file, 0, "skipped"))
            continue

        try:
            rows = read_trajectory_csv(file_path, config.delimiter)
            store.insert_records(
                source_file,
                config.run_identifier,
                config.dataset_date,
                config.area,
                rows,
            )
            store.insert_metadata(
                source_file,
                config.run_identifier,
                config.dataset_date,
                config.area,
                len(rows),
            )
            connection.commit()
            logger.info(
                "Loaded %s rows from %s for run %s",
                len(rows),
                source_file,
                config.run_identifier,
            )
            summaries.append(FileLoadSummary(source_file, len(rows), "loaded"))
        except Exception:
            connection.rollback()
            logger.exception(
                "Failed loading %s for run %s", source_file, config.run_identifier
            )
            raise

    return LoadSummary(summaries)


def read_trajectory_csv(file_path: Path, delimiter: str) -> list[dict[str, str]]:
    with file_path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows = [dict(row) for row in reader]

    if reader.fieldnames is None:
        raise ValueError(f"{file_path} does not include a header row")
    return rows


def connect_from_url(connection_url: str) -> Any:
    parsed = urlparse(connection_url)
    if parsed.scheme == "sqlite":
        database = parsed.path if parsed.path != "/:memory:" else ":memory:"
        return sqlite3.connect(database)
    if parsed.scheme in {"postgres", "postgresql"}:
        import psycopg2

        return psycopg2.connect(connection_url)
    raise ValueError(f"Unsupported database connection scheme: {parsed.scheme}")


def config_from_env() -> IngestionConfig:
    return IngestionConfig(
        data_path=Path(os.environ.get("TRAJECTORY_DATA_PATH", "/opt/airflow/data")),
        file_pattern=os.environ.get("TRAJECTORY_FILE_PATTERN", "*.csv"),
        dataset_date=os.environ.get("DATASET_DATE"),
        area=os.environ.get("DATASET_AREA"),
        run_identifier=os.environ.get("RUN_IDENTIFIER", "manual"),
        delimiter=os.environ.get("TRAJECTORY_DELIMITER", ";"),
    )


def run_from_env() -> LoadSummary:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    connection_url = os.environ.get("WAREHOUSE_CONNECTION_URL") or os.environ.get(
        "AIRFLOW_CONN_WAREHOUSE_POSTGRES"
    )
    if not connection_url:
        raise RuntimeError(
            "Set WAREHOUSE_CONNECTION_URL or AIRFLOW_CONN_WAREHOUSE_POSTGRES"
        )
    connection = connect_from_url(connection_url)
    try:
        return load_trajectory_files(connection, config_from_env())
    finally:
        connection.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load trajectory CSV files into raw tables")
    parser.add_argument("--connection-url", default=os.environ.get("WAREHOUSE_CONNECTION_URL"))
    parser.add_argument("--data-path", default=os.environ.get("TRAJECTORY_DATA_PATH", "data"))
    parser.add_argument("--file-pattern", default=os.environ.get("TRAJECTORY_FILE_PATTERN", "*.csv"))
    parser.add_argument("--dataset-date", default=os.environ.get("DATASET_DATE"))
    parser.add_argument("--area", default=os.environ.get("DATASET_AREA"))
    parser.add_argument("--run-id", default=os.environ.get("RUN_IDENTIFIER", "manual"))
    parser.add_argument("--delimiter", default=os.environ.get("TRAJECTORY_DELIMITER", ";"))
    args = parser.parse_args(argv)

    if not args.connection_url:
        parser.error("--connection-url or WAREHOUSE_CONNECTION_URL is required")

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    connection = connect_from_url(args.connection_url)
    try:
        summary = load_trajectory_files(
            connection,
            IngestionConfig(
                data_path=Path(args.data_path),
                file_pattern=args.file_pattern,
                dataset_date=args.dataset_date,
                area=args.area,
                run_identifier=args.run_id,
                delimiter=args.delimiter,
            ),
        )
    finally:
        connection.close()

    print(json.dumps({"files": [file.__dict__ for file in summary.files]}, indent=2))
    return 0


def _optional_float(value: str | None) -> float | None:
    if value in {None, ""}:
        return None
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
