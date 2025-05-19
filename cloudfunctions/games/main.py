import base64
import functions_framework
from datetime import datetime
import os
import logging
import json
from google.cloud import bigquery


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


PROJECT_ID  = os.getenv("PROJECT_ID", "default_project")
DATASET_ID = os.getenv("BQ_DATASET", "default-dataset")
NBA_GAMES_TABLE = os.getenv("NBA_GAMES_TABLE", "default-table")

bq = bigquery.Client(project=PROJECT_ID)


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None


def transform_game_time(date_time_str):
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M:%S")
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


def transform_season(season):
    try:
        return f"{int(season) - 1}-{str(season)[-2:]}"
    except Exception as e:
        logging.error(f"Error transforming season format: {e}")
        return season


def replace_nulls(data):
    new_data = {}
    for key, value in data.items():
        if value is None:
            new_data[key] = 0
        else:
            new_data[key] = value
    return new_data


def add_win_loss(payload):
    if payload["wins"] == 1:
        payload["win_loss"] = "W"
    elif payload["losses"] == 1:
        payload["win_loss"] = "L"
    else:
        payload["win_loss"] = None
    return payload


def transform_team_id_to_abbr(payload):
    try:
        with open("combined_teams.json", 'r') as f:
            nba_teams = json.load(f)
            nba_teams_dict = {team["team_id_sd"]: team for team in nba_teams}
        
        team_info = nba_teams_dict.get(payload["team_id_sd"], {"abbreviation": "Unknown", "team_name": "Unknown", "team_id_nba": "Unknown", "team_id_sd": "Unknown", "city": "Unknown", "nickname": "Unknown"})
        payload["team_abbr"] = team_info["abbreviation"]
        payload["team_id"] = team_info["team_id_nba"]
        payload["team_name"] = team_info["team_name"]
        payload["home_team"] = team_info["abbreviation"]
        del payload["team_id_sd"]
        visitor_team_info = nba_teams_dict.get(payload["away_team_id_sd"], {"abbreviation": "Unknown", "team_name": "Unknown", "team_id_nba": "Unknown", "team_id_sd": "Unknown", "city": "Unknown", "nickname": "Unknown"})
        payload["away_team"] = visitor_team_info["abbreviation"]
        del payload["away_team_id_sd"]
        return payload
    except Exception as e:
        logging.error(f"Error transforming team IDs: {e}")
        return None


@functions_framework.cloud_event
def callback_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        payload["game_date"] = transform_game_date(payload["game_date"])
        date_parts = extract_date(payload["game_date"])
        payload["year"] = date_parts["year"]
        payload["month"] = date_parts["month"]
        payload["day"] = date_parts["day"]
        payload["date_time"] = transform_game_time(payload["date_time"])
        payload["field_goals_percentage"] = percentage_decimal(payload["field_goals_percentage"])
        payload["two_pointers_percentage"] = percentage_decimal(payload["two_pointers_percentage"])
        payload["three_pointers_percentage"] = percentage_decimal(payload["three_pointers_percentage"])
        payload["free_throws_percentage"] = percentage_decimal(payload["free_throws_percentage"])
        payload["season"] = transform_season(payload["season"])
        payload = transform_team_id_to_abbr(payload)
        payload = add_win_loss(payload)
        payload = replace_nulls(payload)
        del payload["wins"]
        del payload["losses"]
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
        