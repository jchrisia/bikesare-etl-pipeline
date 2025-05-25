# bikeshare_etl_daily.py
import sys
sys.path.append('/opt/airflow/scripts')  #Ensure custom scripts/ folder is in Python path

from airflow import DAG
from airflow.operators.python import PythonOperator, get_current_context
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
from google.cloud import storage, bigquery
from extract_bikeshare import extract_and_upload

PROJECT_ID = "capable-acrobat-388708"
DATASET_NAME = "bikeshare"
EXTERNAL_TABLE = "external_bikeshare_trips"
BUCKET_NAME = "jo-bikeshare-data"

def list_partitioned_uris(**context):
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(BUCKET_NAME)

    blobs = list(bucket.list_blobs(prefix="bikeshare/"))
    dates = set()
    for blob in blobs:
        parts = blob.name.split('/')
        if len(parts) >= 3 and parts[0] == "bikeshare":
            dates.add(parts[1])  # e.g., "2024-06-28"

    uris = [f"gs://{BUCKET_NAME}/bikeshare/{date}/*/data.parquet" for date in sorted(dates)]
    context['ti'].xcom_push(key="external_uris", value=uris)

def run_extract(**context):
    extract_and_upload(context["ds"])

def create_external_table_from_uris(**context):
    uris = context['ti'].xcom_pull(task_ids='list_gcs_parquet_uris', key='external_uris')
    if not uris:
        raise ValueError("No URIs found in XCom.")

    client = bigquery.Client()
    table_id = f"{PROJECT_ID}.{DATASET_NAME}.{EXTERNAL_TABLE}"

    table = bigquery.Table(table_id)
    external_config = bigquery.ExternalConfig("PARQUET")
    external_config.source_uris = uris
    external_config.autodetect = True
    table.external_data_configuration = external_config

    # Overwrite if table exists
    client.delete_table(table_id, not_found_ok=True)
    client.create_table(table)
    print(f"✅ External table created at {table_id} with {len(uris)} URIs.")

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="bikeshare_etl_daily",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["bikeshare", "etl"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract_partitioned_to_gcs",
        python_callable=run_extract,
        provide_context=True,
    )

    list_uris_task = PythonOperator(
        task_id="list_gcs_parquet_uris",
        python_callable=list_partitioned_uris,
        provide_context=True,
    )

    create_external_table = PythonOperator(
        task_id="create_biglake_external_table",
        python_callable=create_external_table_from_uris,
        provide_context=True,
    )

    extract_task >> list_uris_task >> create_external_table
