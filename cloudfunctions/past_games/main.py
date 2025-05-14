import os
import logging
from google.cloud import bigquery
import functions_framework

PROJECT_ID = os.getenv("GCP_PROJECT", "feisty-lamp-442712-m8")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_GAMES_TABLE = os.getenv("BQ_TABLE", "all_games")

bq = bigquery.Client(project=PROJECT_ID)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

@functions_framework.cloud_event
def callback_games(cloud_event):
    bucket_name = cloud_event.data.get("bucket")
    object_name = cloud_event.data.get("name")

    if not object_name or not object_name.endswith(".csv"):
        logging.info(f"Ignoring non-csv file: {object_name}")
        return

    uri = f"gs://{bucket_name}/{object_name}"
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_GAMES_TABLE}"

    logging.info(f"Starting load from {uri} into {table_ref}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        range_partitioning=bigquery.RangePartitioning(
            field="TEAM_ID",
            range_=bigquery.PartitionRange(start=1610612737, end=1610612767, interval=1),
        ),
    )

    try:
        load_job = bq.load_table_from_uri(uri, table_ref, job_config=job_config)
        load_job.result()
        logging.info(f"Loaded {load_job.output_rows} rows into {table_ref}")
    except Exception as e:
        logging.error(f"BigQuery load_job failed: {e}")
        raise

