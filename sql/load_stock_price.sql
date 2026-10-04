BEGIN;

DELETE FROM ATLAS_DB.STAGING.STOCK_PRICE;

COPY INTO ATLAS_DB.STAGING.STOCK_PRICE
FROM @ATLAS_STOCK_PRICE_STAGE/{{ ds }}/
FILE_FORMAT = (
TYPE = CSV
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
);

MERGE INTO ATLAS_DB.CORE.STOCK_PRICE AS target
USING ATLAS_DB.STAGING.STOCK_PRICE AS source
ON target.ticker = source.ticker
AND target.date = source.date

WHEN MATCHED
AND target.fingerprint <> source.fingerprint
THEN UPDATE SET
target.open = source.open,
target.high = source.high,
target.low = source.low,
target.close = source.close,
target.volume = source.volume,
target.ingestion_time = source.ingestion_time,
target.fingerprint = source.fingerprint,
target.daily_change = source.close - source.open,
target.daily_return_pct = ((source.close - source.open) / source.open) * 100

WHEN NOT MATCHED
THEN INSERT (
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
)
VALUES (
source.ticker,
source.date,
source.open,
source.high,
source.low,
source.close,
source.volume,
source.ingestion_time,
source.fingerprint,
source.close - source.open,
((source.close - source.open) / source.open) * 100
);

COMMIT;
