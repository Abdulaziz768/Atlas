from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id='atlas_stock_price'
) as dag:
    start = EmptyOperator(
        task_id="start"
    )
    ingest_stock_price = BashOperator(
        task_id="ingest_stock_price",
        bash_command='python scripts/ingest_stock_price.py',
        cwd='/Users/mohammadabdulaziz/Atlas'
    )

    stock_price_pyspark = BashOperator(
        task_id="stock_price_pyspark",
        bash_command='python scripts/run_stock_price_job.py',
        cwd='/Users/mohammadabdulaziz/Atlas'
    )

    end = EmptyOperator(
        task_id="end"
    )
    start>>ingest_stock_price>>stock_price_pyspark>>end

