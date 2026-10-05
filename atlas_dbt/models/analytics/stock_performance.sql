select
    ticker,

    min(date) as first_date,
    max(date) as latest_date,

    min_by(close, date) as first_close,
    max_by(close, date) as latest_close,

    (
        (max_by(close, date) - min_by(close, date))
        / nullif(min_by(close, date), 0)
    ) * 100 as total_return_pct,

    avg(daily_return_pct) as average_daily_return_pct,

    max(daily_return_pct) as best_day_return_pct,
    min(daily_return_pct) as worst_day_return_pct,

    sum(volume) as total_volume,

    count(*) as trading_days

from {{ ref('stg_stock_price') }}

group by ticker