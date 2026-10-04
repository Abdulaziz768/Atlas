select
ticker,
date,
count(*) as row_count 
from {{ ref('stg_stock_price')}}
group by ticker, date
having count(*) > 1