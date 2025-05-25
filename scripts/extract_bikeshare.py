# extract_bikeshare.py
from google.cloud import bigquery, storage
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
import shutil

def extract_and_upload(ds: str = None):
    bq_client = bigquery.Client()
    gcs_client = storage.Client()
    bucket = gcs_client.bucket("jo-bikeshare-data")

    try:
        run_date = datetime.strptime(ds, "%Y-%m-%d") if ds else datetime.now(timezone.utc)
        target_date = run_date - timedelta(days=1)
    except Exception as e:
        print(f"⚠️ Fallback to simulated date due to error: {e}")
        target_date = datetime(2024, 6, 30, tzinfo=timezone.utc) - timedelta(days=1)

    date_str = target_date.strftime('%Y-%m-%d')
    print(f"🔍 Extracting data for: {date_str}")

    def run_query(date_str):
        query = f"""
            SELECT *
            FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
            WHERE DATE(start_time) = '{date_str}'
        """
        return bq_client.query(query).result().to_dataframe()

    df = run_query(date_str)
    if df.empty:
        print("⚠️ No data found for date. Exiting.")
        return

    df['date'] = pd.to_datetime(df['start_time']).dt.date
    df['hour'] = pd.to_datetime(df['start_time']).dt.hour

    local_path = f"/tmp/bikeshare/{date_str}"
    os.makedirs(local_path, exist_ok=True)

    for hour, group in df.groupby('hour'):
        local_file = f"{local_path}/{hour:02d}_data.parquet"
        group.to_parquet(local_file, index=False)
        gcs_path = f"bikeshare/{date_str}/{hour:02d}/data.parquet"
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_file)
        print(f"✅ Uploaded to: {gcs_path}")
