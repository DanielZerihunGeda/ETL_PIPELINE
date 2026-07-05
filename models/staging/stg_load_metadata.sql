select
    source_file,
    run_identifier,
    dataset_date,
    area,
    row_count,
    loaded_at
from {{ source('raw', 'load_metadata') }}
