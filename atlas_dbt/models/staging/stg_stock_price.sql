select
    ticker,
    date,
    open,
    high,
    low,
    close,
    volume,
    ingestion_time,
    fingerprint,
    daily_change,
    daily_return_pct
from {{ source('atlas_core', 'STOCK_PRICE') }}