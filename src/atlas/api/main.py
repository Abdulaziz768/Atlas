from fastapi import FastAPI, HTTPException

from atlas.api.snowflake import (
    get_stock_performance,
    get_stock_performance_by_ticker,
)


app = FastAPI(
    title="Atlas API",
    description="Financial analytics API powered by Snowflake",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/stocks")
def get_stocks():
    return get_stock_performance()


@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    stock = get_stock_performance_by_ticker(ticker)

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail=f"Stock '{ticker.upper()}' not found",
        )

    return stock
