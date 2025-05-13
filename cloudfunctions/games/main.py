import base64
import functions_framework
from datetime import datetime
import os
import logging
import json
from google.cloud import bigquery


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_GAMES_TABLE = os.getenv("NBA_GAMES_TABLE", "nba_games")

bq = bigquery.Client(project=PROJECT_ID)


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None




# NBA TEAMS
@functions_framework.cloud_event
def callback_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        if "game_date" not in payload or "matchup" not in payload:
            logging.warning("Missing fields.")
            return
        payload["game_date"] = transform_game_date(payload["game_date"])
        # Insert to BigQuery
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_GAMES_TABLE}"
        errors = bq.insert_rows_json(table_ref, [payload])
        if errors:
            logging.error(f"Error inserting into BigQuery: {errors}")
        else:
            logging.info("NBA games inserted into BigQuery sucessfully.")
        logging.info("NBA games processed sucessfully.")
    except Exception as e:
        logging.error(f"Error trying to process NBA games: {e}")
        raise
        