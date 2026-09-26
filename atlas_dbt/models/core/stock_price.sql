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

    close - open as daily_change,

    ((close - open) / open) * 100 as daily_return_pct

from {{ ref('stg_stock_price') }}