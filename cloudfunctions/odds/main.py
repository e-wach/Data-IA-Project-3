import base64
import functions_framework
import os
import logging
import json
from google.cloud import bigquery


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_ODDS_TABLE = os.getenv("NBA_ODDS_TABLE", "nba_odds")

bq = bigquery.Client(project=PROJECT_ID)


# NBA TEAMS
@functions_framework.cloud_event
def callback_odds(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_ODDS_TABLE}"
        errors = bq.insert_rows_json(table_ref, [payload])
        if errors:
            logging.error(f"Error inserting into BigQuery: {errors}")
        else:
            logging.info("Data inserted into BigQuery sucessfully.")
        logging.info("NBA odds processed sucessfully.")
    except Exception as e:
        logging.error(f"Error trying to process NBA odds: {e}")
        raise
        