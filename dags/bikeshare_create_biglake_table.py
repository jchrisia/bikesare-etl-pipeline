#bikeshare_create_biglake_table.py
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Set your values
PROJECT_ID = "capable-acrobat-388708"
DATASET_NAME = "bikeshare"
TABLE_NAME = "external_bikeshare_trips"
BUCKET_NAME = "jo-bikeshare-data"

# Use wildcard to reference partitioned hourly folders
GCS_URI = f"gs://{BUCKET_NAME}/bikeshare/*/*.parquet"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="bikeshare_create_biglake_table",
    default_args=default_args,
    description="Create external BigLake table for Bikeshare data in GCS",
    schedule_interval="@daily",
    start_date=days_ago(1),
    catchup=False,
    tags=["bikeshare", "biglake", "bigquery"],
) as dag:

    create_biglake_table = BigQueryCreateExternalTableOperator(
        task_id="create_biglake_external_table",
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_NAME,
                "tableId": TABLE_NAME,
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [GCS_URI],
                "autodetect": True,
            },
        },
        gcp_conn_id="google_cloud_default",
    )

    create_biglake_table
