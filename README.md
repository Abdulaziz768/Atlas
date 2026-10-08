# Atlas

**End-to-end financial data engineering platform built with Python, AWS, PySpark, Snowflake, dbt, Airflow, FastAPI, and React.**

Atlas is a portfolio Data Engineering project that ingests financial market data, validates and processes it at scale, stores it across layered data platforms, and exposes the resulting analytics through an API and dashboard.

The project is designed around real Data Engineering concerns such as **incremental processing, data quality, quarantine handling, deduplication, idempotent loading, retries, observability, and analytics modeling**.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │   Financial APIs     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Python Ingestion    │
                    │ Retry / Validation  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     AWS S3 Raw      │
                    │   Source Snapshots  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Python Processing   │
                    │ Quality Validation  │
                    └───────┬─────┬───────┘
                            │     │
                     valid  │     │ invalid
                            ▼     ▼
                    ┌──────────┐ ┌─────────────┐
                    │Processed │ │ Quarantine  │
                    │   S3     │ │     S3      │
                    └────┬─────┘ └─────────────┘
                         │
                         ▼
                    ┌─────────────────────┐
                    │      PySpark        │
                    │ Validate / Dedup /  │
                    │ Transform / Clean   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      AWS S3         │
                    │    Clean Output     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Snowflake       │
                    │                     │
                    │ RAW → STAGING → CORE│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │        dbt          │
                    │ Analytics Models +  │
                    │ Data Tests           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │   Analytics API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      React          │
                    │     Dashboard       │
                    └─────────────────────┘

              Airflow orchestrates the pipeline
              GitHub Actions runs automated tests
```

---

## What Atlas Does

Atlas currently contains an end-to-end **stock-price data pipeline** as its main vertical slice.

The pipeline:

1. Retrieves historical stock-price data from a financial API.
2. Handles API failures and retries.
3. Stores the source response as a raw S3 snapshot.
4. Applies data-quality rules.
5. Separates invalid records into a quarantine area.
6. Writes valid records to the processed S3 layer.
7. Uses PySpark for scalable transformation and deduplication.
8. Writes cleaned data back to S3.
9. Loads the data into Snowflake staging.
10. Uses a `MERGE` to maintain the Snowflake core table.
11. Builds analytics models with dbt.
12. Exposes analytics through FastAPI.
13. Displays the results through a React dashboard.
14. Orchestrates the workflow with Airflow.

---

## Data Engineering Design

### Raw Data

Raw source responses are stored in S3 using date-partitioned paths.

```text
raw/
└── stock_price/
    └── <processing_date>/
        └── <ticker>.json
```

The raw layer preserves the source response before downstream processing.

Atlas currently uses **date-partitioned raw snapshots** rather than claiming full historical immutability of every individual API response.

---

### Data Quality

Atlas validates stock-price records before they enter downstream processing.

Examples of validation rules include:

- ticker must exist
- trading date must exist
- open/high/low/close must exist
- prices cannot be negative
- volume cannot be negative
- high cannot be lower than open or close
- low cannot be higher than open or close

Invalid records are isolated in a quarantine location rather than silently discarded.

```text
                    Processed Records
                           │
                           ▼
                    Data Quality Check
                       /         \
                    valid       invalid
                     │             │
                     ▼             ▼
                  Clean         Quarantine
```

---

## PySpark Processing

PySpark is used for the larger transformation stage.

The stock-price transformation performs:

- schema handling
- data validation
- deduplication
- fingerprint generation
- ordering by ingestion time
- clean-output generation

### Deduplication

The business key for a daily stock-price record is:

```text
ticker + date
```

When multiple records exist for the same business key, Atlas retains the record with the latest `ingestion_time`.

This makes the downstream Snowflake load deterministic.

---

## Fingerprinting

Atlas generates a SHA-256 fingerprint from the relevant stock-price values.

The fingerprint allows the Snowflake load process to distinguish between:

```text
Same ticker + same date + same values
```

and:

```text
Same ticker + same date + changed values
```

This supports change detection during the Snowflake `MERGE`.

---

## Snowflake Data Model

Snowflake is organized into logical layers:

```text
STAGING
   │
   ▼
CORE
   │
   ▼
ANALYTICS
```

### STAGING

Temporary load area for the current pipeline execution.

The staging table is cleared before the daily load.

### CORE

Contains the cleaned stock-price records.

Atlas uses a `MERGE` based on:

```text
ticker + date
```

This provides idempotent loading behavior.

If the same data is loaded again, duplicate core records are not created.

If the fingerprint changes, the existing record can be updated.

### ANALYTICS

Contains business-facing analytical models generated through dbt.

---

## dbt

dbt is used to create the analytics layer and enforce data quality through automated tests.

Current stock-price modeling includes:

```text
STAGING
   │
   ▼
stg_stock_price
   │
   ▼
stock_performance
```

The analytics model calculates metrics such as:

- first trading date
- latest trading date
- first close
- latest close
- total return
- average daily return
- best trading day
- worst trading day
- total volume
- trading-day count

The dbt pipeline also runs data tests as part of the Airflow workflow.

---

## Airflow

Airflow orchestrates the end-to-end stock-price workflow.

```text
start
  ↓
ingest_stock_price
  ↓
stock_price_pyspark
  ↓
load_to_snowflake
  ↓
dbt_build
  ↓
end
```

The ingestion task includes retries and a retry delay to handle transient API failures.

The workflow is designed so that a failed upstream stage prevents downstream stages from executing against incomplete data.

---

## FastAPI

Atlas exposes the analytics layer through a small REST API.

### Health

```text
GET /health
```

### All stocks

```text
GET /stocks
```

### Individual stock

```text
GET /stocks/{ticker}
```

Example:

```text
GET /stocks/AAPL
```

The API reads the analytical results from Snowflake rather than directly querying the financial API.

---

## React Dashboard

Atlas includes a lightweight React dashboard built with Vite and Recharts.

The dashboard provides:

- ticker selection
- date range
- latest close
- total return
- trading-day count
- total volume
- first vs latest close comparison
- average daily return
- best trading day
- worst trading day

The dashboard is intentionally kept lightweight because its purpose is to demonstrate the complete data flow rather than serve as a production frontend.

---

## Testing

Atlas uses `pytest` for automated testing.

The test suite covers important components including:

- API endpoints
- Snowflake access layer
- company pipeline
- S3 storage abstraction
- stock-price quality rules
- PySpark reader
- PySpark transformations
- deduplication
- fingerprinting

S3 storage tests use a fake S3 client, so unit tests do not require real AWS operations.

The project also runs automated tests through GitHub Actions.

---

## CI/CD

GitHub Actions runs the Python test suite on pushes and pull requests.

The CI workflow:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Sets up Java 17 for PySpark.
4. Installs Atlas.
5. Runs the test suite.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Processing | PySpark 4.2 |
| Object Storage | AWS S3 |
| Data Warehouse | Snowflake |
| Transformation / Analytics | dbt |
| Orchestration | Apache Airflow |
| API | FastAPI |
| Frontend | React + Vite |
| Charts | Recharts |
| Testing | pytest |
| CI | GitHub Actions |
| Containers | Docker |
| Version Control | Git / GitHub |

---

## Project Structure

```text
Atlas/
│
├── src/
│   └── atlas/
│       ├── api/
│       ├── ingestion/
│       ├── pipelines/
│       ├── quality/
│       ├── storage/
│       ├── transformation/
│       └── spark/
│
├── scripts/
│   ├── ingest_stock_price.py
│   └── run_stock_price_job.py
│
├── dags/
│   └── stock_price.py
│
├── sql/
│   └── load_stock_price.sql
│
├── atlas_dbt/
│   ├── models/
│   │   ├── staging/
│   │   └── analytics/
│   └── tests/
│
├── frontend/
│   └── React dashboard
│
├── tests/
│
├── .github/
│   └── workflows/
│
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

---

## Key Engineering Concepts Demonstrated

Atlas was designed to demonstrate practical Data Engineering concepts rather than simply collecting technologies.

### Incremental / partitioned processing

Data is organized using processing-date partitions so pipeline executions can operate on defined slices of data.

### Idempotency

Snowflake uses a business-key `MERGE` to prevent duplicate core records when the same data is processed repeatedly.

### Deduplication

Multiple records for the same `ticker + date` are resolved using the latest ingestion timestamp.

### Data Quality

Invalid financial records are detected using explicit domain rules.

### Quarantine

Bad records are isolated rather than silently dropped.

### Failure Handling

API failures propagate to Airflow and can trigger task retries.

### Observability

The processing jobs report row counts and validation results to make pipeline behavior visible.

### Layered Architecture

Raw, processed, clean, staging, core, and analytics layers separate ingestion concerns from analytical consumption.

### Separation of Concerns

The project separates:

```text
Ingestion
Storage
Quality
Transformation
Orchestration
Warehouse Loading
Analytics
API
Presentation
```

---

## Running the Project

### Python environment

Create and activate a Python 3.12 environment, then install the project dependencies.

```bash
pip install -e ".[test]"
```

### Run tests

```bash
python -m pytest tests --ignore=tests/integration
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The React development server runs on the Vite development port.

The FastAPI backend runs separately.

---

## Configuration

Atlas uses environment-based configuration for credentials and connection details.

Sensitive credentials should be provided through environment variables or local configuration files and should **not** be committed to Git.

An example configuration file is provided in:

```text
.env.example
```

---

## Current Scope

Atlas is intentionally a portfolio-scale implementation.

It focuses on demonstrating:

- reliable ingestion
- cloud object storage
- distributed processing
- warehouse loading
- analytical modeling
- orchestration
- API serving
- dashboard consumption
- automated testing

It does not attempt to reproduce the infrastructure scale of a production financial-data platform.

---

## Future Improvements

Possible future improvements include:

- stronger raw-data versioning
- configurable frontend API environments
- more advanced monitoring
- additional financial datasets
- production-grade authentication
- warehouse performance optimization

These are intentionally outside the current V1 scope.

---

## Author

**Abdulaziz Mohammad**

Data Engineer | Python | SQL | AWS | PySpark | Snowflake | dbt | Airflow