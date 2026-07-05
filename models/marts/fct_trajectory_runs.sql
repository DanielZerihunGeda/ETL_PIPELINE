with trajectory_records as (
    select *
    from {{ ref('stg_trajectory_records') }}
),

load_metadata as (
    select *
    from {{ ref('stg_load_metadata') }}
),

record_metrics as (
    select
        source_file,
        run_identifier,
        dataset_date,
        area,
        count(*) as trajectory_record_count,
        count(distinct track_id) as vehicle_count,
        avg(avg_speed) as average_track_speed,
        avg(observed_speed) as average_observed_speed,
        min(observed_at) as first_observed_at,
        max(observed_at) as last_observed_at,
        min(loaded_at) as first_loaded_at,
        max(loaded_at) as last_loaded_at
    from trajectory_records
    group by 1, 2, 3, 4
)

select
    record_metrics.source_file,
    record_metrics.run_identifier,
    record_metrics.dataset_date,
    record_metrics.area,
    record_metrics.trajectory_record_count,
    record_metrics.vehicle_count,
    record_metrics.average_track_speed,
    record_metrics.average_observed_speed,
    record_metrics.first_observed_at,
    record_metrics.last_observed_at,
    record_metrics.first_loaded_at,
    record_metrics.last_loaded_at,
    load_metadata.row_count as metadata_row_count
from record_metrics
left join load_metadata
    on record_metrics.source_file = load_metadata.source_file
    and record_metrics.run_identifier = load_metadata.run_identifier
