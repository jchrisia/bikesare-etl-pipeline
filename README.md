# Project Overview
This project implements a daily ETL pipeline using Apache Airflow to extract Austin Bikeshare trip data from BigQuery, partition and store it in Google Cloud Storage (GCS) as Parquet files, and create an external BigLake table for analytical querying. The pipeline is containerized using Docker and uses Airflow's DAGs to orchestrate daily updates and data validation.

# Observation 
The pipeline simulates daily ETL updates. However, upon inspecting the source data, it was found that the most recent records in bigquery-public-data.austin_bikeshare.bikeshare_trips are from 2024-06-30.

Since the extraction script is designed to pull data from the previous day, running the DAG beyond this point results in failure due to the absence of new data.

While the code is intended to run daily, provided the raw data is available every day, a workaround is implemented for simulation purposes. This involves using backfill commands for specific dates, as detailed later in this section.

## Notes 
Please note that the Task 5 query is in a separate file, and for this assignment, I am using macOS.


# What this repo contains
bikeshare-etl-pipeline/
dags/
  bikeshare_etl_daily.py : Extracts daily data, uploads to GCS, and creates/refreshes external BigLake table.
  bikeshare_create_biglake_table.py : A standalone DAG to create the external table once.
scripts/
  1.Find the total number of trips for each day.sql 
  2.Calculate the average trip duration for each day.sql
  3.Identify the top 5 stations with the highest number of trip starts.sql
  4.Find the average number of trips per hour of the day.sql
  5.Determine the most common trip route (start station to end station).sql
  6.Calculate the number of trips each month.sql
  7.Find the station with the longest average trip duration.sql
  8.Find the busiest hour of the day (most trips started).sql
  9.Identify the day with the highest number of trips.sql
  extract_bikeshare.py : Extracts trip data from public data to partitions
Dockerfile
docker-compose.yaml
requirements.txt
README.md


# Prerequisites
## Docker and Docker Compose installed
- **macOS**: [Install Docker Desktop](https://docs.docker.com/desktop/)
- **Linux/Ubuntu**: [Install Docker Compose](https://docs.docker.com/compose/install/) and [Install Docker Engine](https://docs.docker.com/engine/install/)
- **Windows**: Windows Subsystem for Linux (WSL) to run the bash based command. Please follow [Windows Subsystem for Linux Installation (WSL)](https://docs.docker.com/docker-for-windows/wsl/) and [Using Docker in WSL 2](https://code.visualstudio.com/blogs/2020/03/02/docker-in-wsl2), to get started. Otherwise, [Install Docker Desktop](https://docs.docker.com/desktop/)

## Google Cloud Services 
- Create a Google Cloud Project <https://console.cloud.google.com/>
- Enable the BigQuery API for the project
- Verify access to the BigQuery public dataset `bigquery-public-data.austin_bikeshare.bikeshare_trips` by running the following query:
```sql
SELECT * 
FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
LIMIT 10;
```
- Create a bucket in Google Cloud Storage (for this assignment, the bucket name is `jo-bikeshare-data`)

### Service Account
- Create a Service Account and download the Service Account key.
- Place the downloaded key at: `bikeshare-etl-pipeline/scripts/service_account.json`.
- Assign the following roles to the Service Account: BigQuery User, BigQuery Data Viewer, Storage Object Admin


# Get Started 
## Setup and Run from my project repo
### Step one: place the project files
Clone or place the project files and navigate into the directory:
```bash
cd bikeshare-etl-pipeline
```

### Step two: Build the Docker Image (using the Dockerfile)
Build the custom Airflow image that includes all your dependencies:
```bash
docker-compose build
```
### Step three: Initialize the Airflow Database
Run the following command to initialize the Airflow environment (create metadata DB, user, etc.):
```bash
docker-compose run --rm airflow-init
```

### Step four: Start All Airflow Services
Use Docker Compose to bring up the entire Airflow stack:
```bash
docker-compose up -d
```


### Step five: Accessing the Airflow UI
Once everything is up and running, access the Airflow web UI at:
<http://localhost:8081/>

The default login is:
Username: airflow
Password: airflow

### Step six: Running the ETL Script
1. Running an Interactive Shell in the Airflow Scheduler Container
```bash
docker exec -it airflow-docker-test-airflow-scheduler-1 bash
```

2. As the latest data is 2024-06-30 we use backfill code command.
use this command to test extract and store file for one date
```bash
airflow dags backfill -s 2024-06-29 -e 2024-06-29 bikeshare_etl_daily --reset-dagruns
```

3. use this command to test extract and store file for multiple dates to check if the `external_bikeshare_trips store` table contains all partitioned data
```bash
airflow dags backfill -s 2024-06-25 -e 2024-06-29 bikeshare_etl_daily --reset-dagruns
```

### Step seven: Verify the parquet is stored in the `external_bikeshare_trips`
- Open Google Cloud Console and navigate to BigQuery.
- In the `external_bikeshare_trips` table, go to the Details tab.
- Check the Source URI(s) to confirm that Parquet files for the dates 2024-06-25 to 2024-06-29 are present.
Example GCS Partition Structure:
`gs://jo-bikeshare-data/bikeshare/2024-06-29/15/data.parquet`
`gs://jo-bikeshare-data/bikeshare/2024-06-29/16/data.parquet`
- See SQL queries 1–9 under `scripts/` for analytical tasks used in Task 5




## Set Up Environment From Scratch 
# Step one : Create a Project Directory
```bash
mkdir bikeshare-etl-pipeline
cd bikeshare-etl-pipeline
```

# Step two : Create Required Project Files
1. Create the following files in the root of `bikeshare-etl-pipeline/`:
- `Dockerfile`: builds a custom Airflow image with Python dependencies and Google Cloud SDK
- `docker-compose.yaml`: defines all services (webserver, scheduler, worker, PostgreSQL, Redis)
- `requirements.txt`: lists Python packages to be installed in the container
2. Ensure `docker-compose.yaml` mounts your service account and sets the GCP credential path:
```yaml
    volumes:
    - ./scripts/service_account.json:/opt/yourpath/yourpath/service_account.json

    environment:
      <<: *airflow-common-env
      GOOGLE_APPLICATION_CREDENTIALS: /opt/yourpath/yourpath/service_account.json
```
This ensures that each Airflow service can authenticate with Google Cloud using the mounted service account credentials.

# Step three : Build the Docker Image
From the root directory, run:
```bash
docker-compose build
```

# Step four: Set Airflow Environment Variables
Run the queries:
```bash
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
```
On Windows, Manually create a .env file and add:
```ini
AIRFLOW_UID=50000
AIRFLOW_GID=0
```


# Step five : Initialize the Airflow Environment
Run the following command to initialize Airflow’s metadata database and default configuration:
```bash
docker-compose run --rm airflow-init
```

# Step six : Start Airflow
Start all Airflow services (webserver, scheduler, worker, Redis, and PostgreSQL):
```bash
docker-compose up
```

# Step seven : Access Airflow UI
Visit http://localhost:8081

Default credentials:
Username: airflow
Password: airflow

# Step eight : Write Script for Data Extraction and Storage (Task 1) and Test It
1. Refer to `extract_bikeshare.py`
2. Place it under `scripts/`
3. Run the script to test:
```bash
docker exec -it airflow-docker-test-airflow-scheduler-1 python /opt/airflow/scripts/extract_bikeshare.py
```
4. Verify if the Parquet data is stored in Google Cloud Storage via the Console or with:
```bash
gsutil ls gs://your-bucket-name/bikeshare/YYYY-MM-DD/HH/ 
```


# Step nine : Write Script for creating biglake table (Task2) and test it
1. Refer to `bikeshare_create_biglake_table.py`
2. Place it under `dags/`
3. Trigger the DAG manually to test:
```bash
airflow dags trigger bikeshare_create_biglake_table
```
4. Check BigQuery Console and try query 
```sql
SELECT * FROM `capable-acrobat-388708.bikeshare.external_bikeshare_trips` LIMIT 10;
```

# Step ten: Write script to automate the ETL (task 3) and test it
1. Refer to `bikeshare_etl_daily.py`
2. Place it under `dags/`

## To Test
### Restart Docker to apply new code (if necessary):
```bash
docker-compose down
docker-compose up -d --build
```
### Open an interactive shell inside the Airflow scheduler container:
```bash
docker exec -it airflow-docker-test-airflow-scheduler-1 bash
```
### Backfill to simulate daily pipeline runs
Since the latest data is up to 2024-06-30, use backfill to simulate historical runs.
#### Run for a single date
```bash
airflow dags backfill -s 2024-06-29 -e 2024-06-29 bikeshare_etl_daily --reset-dagruns
```

#### Run for multiple dates to validate partition handling:
```bash
airflow dags backfill -s 2024-06-25 -e 2024-06-29 bikeshare_etl_daily --reset-dagruns
```
This will validate that extracted data is correctly stored in partitioned folders and reflected in the external BigLake table.

#### Step ten: Verify the parquet is stored in the `external_bikeshare_trips`
1. Open Google Cloud Console and navigate to BigQuery.
2. In the `external_bikeshare_trips` table, go to the Details tab.
3. Check the Source URI(s) to confirm that Parquet files for the dates 2024-06-25 to 2024-06-29 are present.
4. Use the SQL queries from Task 5 to perform data analysis on the external table.

# Troubleshooting
The following section contains errors you may encounter when running `bikeshare_etl_daily.py`

## DAG Fails with "NO Data Found"
cause: The ETL script extracts data for the previous day. If the source dataset (`austin_bikeshare.bikeshare_trips`) has no records for that date, the task will fail.

Solution:
1. Use backfill to simulate runs with existing data (latest available: 2024-06-30).
2. Example (single day):
```bash
airflow dags backfill -s 2024-06-29 -e 2024-06-29 bikeshare_etl_daily --reset-dagruns
```

## Google Cloud Authentication Errors
Cause: Airflow services can't find or access the service account key.

Solution:
1. Make sure `service_account.json` is correctly mounted in `docker-compose.yaml`:
```yaml
volumes:
  - ./scripts/service_account.json:/opt/yourpath/yourpath/service_account.json
environment:
  GOOGLE_APPLICATION_CREDENTIALS: /opt/yourpath/yourpath/service_account.json
```
2. Check the service account has these roles:
- BigQuery User
- BigQuery Data Viewer
- Storage Object Admin

## Airflow Web UI Not Accessible
Cause: Airflow container is not running or port conflict.

Solution:
1. Check if the container is running:
```bash
docker ps
```
2. If not, restart Airflow:
```bash
docker-compose down
docker-compose up -d --build
```
3. Ensure you're accessing: <http://localhost:8081>

## Parquet Files Not Found in GCS
Cause: Upload failed or incorrect GCS path.

Solution:
1. Check task logs in Airflow UI (`extract_bikeshare_to_gcs`).
2. Verify file presence using:
```bash
gsutil ls gs://<your-bucket-name>/bikeshare/YYYY-MM-DD/HH/
```
3. Ensure partitioned files are stored in this format:
`gs://jo-bikeshare-data/bikeshare/2024-06-29/15/data.parquet`


## BigLake Table Shows No Data
Cause: No valid Parquet files were found at the specified source URIs.

Solution:
1. Confirm that the DAG bikeshare_etl_daily or bikeshare_create_biglake_table ran successfully in the Airflow UI.
2. In the BigQuery Console:
  - Go to your dataset > external_bikeshare_trips
  - Open the Details tab
  - Check the listed External data configuration >> Source URIs
3. Use gsutil to ensure the paths actually contain data:
```bash
gsutil ls gs://jo-bikeshare-data/bikeshare/2024-06-29/15/
```
4. Ensure that your sourceUris pattern in the external table includes wildcards if needed:
```python
"sourceUris": ["gs://jo-bikeshare-data/bikeshare/*/*/*.parquet"]
```
5. Make sure the Parquet files match the expected schema of the external table. Mismatches in column names or types will result in no readable data.
6. If needed, inspect logs in Airflow UI:
  - Go to DAGs > bikeshare_etl_daily > specific run > task create_biglake_external_table > View Log.