from datetime import timedelta, datetime
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.snowflake.operators.snowflake import SQLExecuteQueryOperator

with DAG(
    dag_id='atlas_stock_price',
    schedule='0 6 * * *',
    start_date=datetime(2026, 9, 27),
    catchup=False,
    template_searchpath='/opt/atlas/sql'
) as dag:
    
    start = EmptyOperator(
        task_id="start"
    )

    load_to_snowflake = SQLExecuteQueryOperator(
        task_id="load_to_snowflake",
        conn_id="atlas_snowflake",
        sql='load_stock_price.sql',
    )   

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "dbt build "
            "--project-dir {{ var.value.atlas_project_path }}/atlas_dbt "
            "--profiles-dir {{ var.value.atlas_project_path }}/atlas_dbt"
        ),
        cwd="{{ var.value.atlas_project_path }}",
    )

    ingest_stock_price = BashOperator(
        task_id="ingest_stock_price",
        bash_command='python scripts/ingest_stock_price.py',
        cwd='{{ var.value.atlas_project_path }}',
        retries=3,
        retry_delay=timedelta(minutes=5)
    )

    stock_price_pyspark = BashOperator(
        task_id="stock_price_pyspark",
        bash_command='python scripts/run_stock_price_job.py',
        cwd='{{ var.value.atlas_project_path }}'
    )

    end = EmptyOperator(
        task_id="end"
    )

    start>>ingest_stock_price>>stock_price_pyspark>>load_to_snowflake>>dbt_build>>end

