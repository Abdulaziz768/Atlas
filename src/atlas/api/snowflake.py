import snowflake.connector

from atlas.config.settings import (
    SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_USER,
    SNOWFLAKE_PASSWORD,
    SNOWFLAKE_DATABASE,
    SNOWFLAKE_SCHEMA,
    SNOWFLAKE_WAREHOUSE,
)


def get_connection():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        warehouse=SNOWFLAKE_WAREHOUSE,
    )


def get_stock_performance():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                ticker,
                first_date,
                latest_date,
                first_close,
                latest_close,
                total_return_pct,
                average_daily_return_pct,
                best_day_return_pct,
                worst_day_return_pct,
                total_volume,
                trading_days
            FROM STOCK_PERFORMANCE
            ORDER BY ticker
            """
        )

        columns = [column[0].lower() for column in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    finally:
        connection.close()


def get_stock_performance_by_ticker(ticker: str):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                ticker,
                first_date,
                latest_date,
                first_close,
                latest_close,
                total_return_pct,
                average_daily_return_pct,
                best_day_return_pct,
                worst_day_return_pct,
                total_volume,
                trading_days
            FROM STOCK_PERFORMANCE
            WHERE ticker = %s
            """,
            (ticker.upper(),),
        )

        columns = [column[0].lower() for column in cursor.description]
        row = cursor.fetchone()

        if row is None:
            return None

        return dict(zip(columns, row))

    finally:
        connection.close()
