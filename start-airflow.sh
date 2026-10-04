#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "Starting Atlas Airflow..."
echo "Project: $PWD"

# Load Atlas environment variables
set -a
source .env
set +a

# Always use Atlas DAGs
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/dags"

echo ""
echo "Airflow DAG folder:"
airflow config get-value core dags_folder

echo ""
echo "Checking Atlas DAG..."
airflow dags list | grep atlas_stock_price

echo ""
echo "Starting scheduler..."
airflow scheduler &
SCHEDULER_PID=$!

echo "Scheduler PID: $SCHEDULER_PID"

echo ""
echo "Starting API server..."
airflow api-server &
API_PID=$!

echo "API server PID: $API_PID"

echo ""
echo "Atlas Airflow is running."
echo "Scheduler PID: $SCHEDULER_PID"
echo "API PID:       $API_PID"
echo ""

trap 'echo ""; echo "Stopping Atlas Airflow..."; kill $SCHEDULER_PID $API_PID 2>/dev/null || true' EXIT

wait
