select
    ticker,
    date,
    open,
    high,
    low,
    close,
    volume,
    ingestion_time,
    fingerprint
from {{ source('atlas_staging', 'STOCK_PRICE') }}