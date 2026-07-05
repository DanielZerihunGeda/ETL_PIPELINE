CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS raw.load_metadata (
    id bigserial PRIMARY KEY,
    source_file text NOT NULL,
    run_identifier text NOT NULL,
    dataset_date date,
    area text,
    row_count integer NOT NULL DEFAULT 0,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source_file, run_identifier)
);

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
);
