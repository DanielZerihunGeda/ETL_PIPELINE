with source_records as (
    select *
    from {{ source('raw', 'trajectory_records') }}
)

select
    source_file,
    run_identifier,
    dataset_date,
    area,
    row_number,
    raw_payload,
    nullif(track_id, '') as track_id,
    nullif(vehicle_type, '') as vehicle_type,
    traveled_distance,
    avg_speed,
    nullif(raw_payload ->> 'lat', '')::numeric as latitude,
    nullif(raw_payload ->> 'lon', '')::numeric as longitude,
    nullif(raw_payload ->> 'speed', '')::numeric as observed_speed,
    nullif(raw_payload ->> 'lon_acc', '')::numeric as longitude_accuracy,
    nullif(raw_payload ->> 'lat_acc', '')::numeric as latitude_accuracy,
    nullif(raw_payload ->> 'time', '')::timestamp as observed_at,
    loaded_at
from source_records
