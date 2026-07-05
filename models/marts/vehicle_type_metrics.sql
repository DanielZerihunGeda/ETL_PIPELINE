select
    dataset_date,
    area,
    run_identifier,
    vehicle_type,
    count(*) as trajectory_record_count,
    count(distinct track_id) as vehicle_count,
    avg(avg_speed) as average_track_speed,
    avg(observed_speed) as average_observed_speed,
    min(observed_at) as first_observed_at,
    max(observed_at) as last_observed_at
from {{ ref('stg_trajectory_records') }}
group by 1, 2, 3, 4
