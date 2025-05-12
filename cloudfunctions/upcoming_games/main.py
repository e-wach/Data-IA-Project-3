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
NBA_GAMES_WEEK_TABLE = os.getenv("NBA_GAMES_WEEK_TABLE", "nba_games_week")

bq = bigquery.Client(project=PROJECT_ID)


def remove_fields(message):
    fields_remove = [
        "GameEndDateTime", "Day", "StadiumID", "Updated", "GlobalGameID", "GlobalAwayTeamID", 
        "GlobalHomeTeamID", "IsClosed", "NeutralVenue", "DateTimeUTC", "SeriesInfo"
    ]
    for field in fields_remove:
        if field in message:
            del message[field]
    return message

def transform_season(season):
    try:
        return f"{int(season) - 1}-{str(season)[-2:]}"
    except Exception as e:
        logging.error(f"Error transforming season format: {e}")
        return season


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None
    
def transform_time(datetime_str):
    try:
        if datetime_str is None:
            return "tbd"
        return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S").strftime("%H:%M:%S")
    except Exception as e:
        logging.warning(f"Error transforming DateTime: {e}")
        return "tbd"

def replace_null(payload):
    return {k: (0 if v is None else v) for k, v in payload.items()}
    

def transform_team_id_to_abbr(payload):
    try:
        with open("combined_teams.json", 'r') as f:
            nba_teams = json.load(f)
            nba_teams_dict = {team["team_id_sd"]: team for team in nba_teams}  # Usamos team_id_sd como clave
        
        home_team_info = nba_teams_dict.get(payload["HomeTeamID"], {"abbreviation": "Unknown", "team_name": "Unknown", "team_id_nba": "Unknown", "team_id_sd": "Unknown", "city": "Unknown", "nickname": "Unknown"})
        payload["home_team_abbr"] = home_team_info["abbreviation"]
        del payload["HomeTeam"]
        # payload["home_team_name"] = home_team_info["team_name"]
        payload["home_team_id_nba"] = home_team_info["team_id_nba"]
        # payload["home_team_id_sd"] = home_team_info["team_id_sd"]
        # payload["home_team_nickname"] = home_team_info["nickname"]

        visitor_team_info = nba_teams_dict.get(payload["AwayTeamID"], {"abbreviation": "Unknown", "team_name": "Unknown", "team_id_nba": "Unknown", "team_id_sd": "Unknown", "city": "Unknown", "nickname": "Unknown"})
        payload["away_team_id_nba"] = visitor_team_info["team_id_nba"]
        # payload["away_team_id_sd"] = visitor_team_info["team_id_sd"]
        payload["away_team_abbr"] = visitor_team_info["abbreviation"]
        del payload["AwayTeam"]
        # payload["visitor_team_name"] = visitor_team_info["team_name"]
        payload["away_team_nickname"] = visitor_team_info["nickname"]
        # payload["away_team_id"] = payload.pop("AwayTeamID")
        # payload["away_team"] = payload.pop("AwayTeam")

        return payload

    except Exception as e:
        logging.error(f"Error transforming team IDs: {e}")
        return None

@functions_framework.cloud_event
def callback_upcoming_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        remove_fields(payload)
        payload["DateTime"] = transform_time(payload["DateTime"])
        payload["GAME_DATE"] = transform_game_date(payload["GAME_DATE"])
        payload["Season"] = transform_season(payload["Season"])
        payload = transform_team_id_to_abbr(payload)
        payload = replace_null(payload)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_GAMES_WEEK_TABLE}"
        errors = bq.insert_rows_json(table_ref, [payload])
        if errors:
            logging.error(f"Error inserting into BigQuery: {errors}")
        else:
            logging.info("Data inserted into BigQuery sucessfully.")
        logging.info("NBA upcoming games processed sucessfully.")
    except Exception as e:
        logging.error(f"Error trying to process NBA upcoming teams: {e}")
        raise
        