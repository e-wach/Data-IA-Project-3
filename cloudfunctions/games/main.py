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
        return datetime.strptime(game_date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None


def transform_game_time(date_time_str):
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
    except ValueError:
        logging.warning(f"Invalid datetime format: {date_time_str}")
        return None


def extract_date(game_date):
    try:
        dt = datetime.strptime(game_date, "%Y-%m-%d")
        return {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day
        }
    except ValueError:
        logging.warning(f"Invalid format date: {game_date}")
        return {
            "year": 0,
            "month": 0,
            "day": 0
        }


def percentage_decimal(percentage):
    try:
        return percentage / 100
    except (ValueError, AttributeError):
        logging.warning(f"Invalid percentage value: {percentage}")
        return None


def replace_nulls(data):
    new_data = {}
    for key, value in data.items():
        if value is None:
            new_data[key] = 0
        else:
            new_data[key] = value
    return new_data


# NBA TEAMS
@functions_framework.cloud_event
def callback_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        payload["game_date"] = transform_game_date(payload["game_date"])
        date_parts = extract_date(payload["game_date"])
        payload["game_year"] = date_parts["year"]
        payload["game_month"] = date_parts["month"]
        payload["game_day"] = date_parts["day"]
        payload["date_time"] = transform_game_time(payload["date_time"])
        payload["field_goals_percentage"] = percentage_decimal(payload["field_goals_percentage"])
        payload["two_pointers_percentage"] = percentage_decimal(payload["two_pointers_percentage"])
        payload["three_pointers_percentage"] = percentage_decimal(payload["three_pointers_percentage"])
        payload["free_throws_percentage"] = percentage_decimal(payload["free_throws_percentage"])
        payload = replace_nulls(payload)
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
        