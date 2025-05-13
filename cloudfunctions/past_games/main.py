import os
import logging
from google.cloud import bigquery
import functions_framework

PROJECT_ID = os.getenv("GCP_PROJECT", "western-mix-459018-g4")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_GAMES_TABLE = os.getenv("BQ_TABLE", "all_games")

bq = bigquery.Client(project=PROJECT_ID)

logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s %(levelname)s %(message)s",
)

@functions_framework.cloud_event
def callback_games(cloud_event):

    bucket_name = cloud_event.data.get("bucket")
    object_name = cloud_event.data.get("name")

    if not object_name or not object_name.endswith(".ndjson"):
        logging.info(f"Ignoring non-ndjson file: {object_name}")
        return

    uri = f"gs://{bucket_name}/{object_name}"
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_GAMES_TABLE}"

    logging.info(f"Starting load from {uri} into {table_ref}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        autodetect=True,
        time_partitioning=bigquery.TimePartitioning(field="GAME_DATE"),
    )

    load_job = bq.load_table_from_uri(uri, table_ref, job_config=job_config)
    try:
        load_job.result()  
        logging.info(f"Loaded {load_job.output_rows} rows into {table_ref}")
    except Exception as e:
        logging.error(f"BigQuery load_job failed: {e}")
        raise
