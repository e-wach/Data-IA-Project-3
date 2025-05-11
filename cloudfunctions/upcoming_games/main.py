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
        "GAME_DATE_EST", "GAME_SEQUENCE", "GAMECODE", "LIVE_PERIOD", "LIVE_PC_TIME",
        "NATL_TV_BROADCASTER_ABBREVIATION", "HOME_TV_BROADCASTER_ABBREVIATION", 
        "AWAY_TV_BROADCASTER_ABBREVIATION", "LIVE_PERIOD_TIME_BCAST", 
        "ARENA_NAME", "WH_STATUS", "WNBA_COMMISSIONER_FLAG"
    ]
    for field in fields_remove:
        if field in message:
            del message[field]
    return message

def transform_season(season):
    try:
        return f"{season}-{str(int(season) + 1)[2:]}"
    except Exception as e:
        logging.error(f"Error transforming season format: {e}")
        return season


def transform_team_id_to_abbr(payload):
    try:
        with open("nba_teams.json", 'r') as f:
            nba_teams = json.load(f)
            nba_teams_dict = {team["team_id"]: team for team in nba_teams}
            logging.debug(f"Datos cargados desde JSON: {nba_teams}") 
        home_team_info = nba_teams_dict.get(payload["HOME_TEAM_ID"], {"abbreviation": "Unknown", "team_name": "Unknown"})
        payload["team_abbr"] = home_team_info["abbreviation"]
        payload["team_name"] = home_team_info["team_name"]
        payload["team_id"] = payload.pop("HOME_TEAM_ID") ##### En la tabla de games, el team_id es siempre el equipo que juega en casa

        visitor_team_info = nba_teams_dict.get(payload["VISITOR_TEAM_ID"], {"abbreviation": "Unknown", "team_name": "Unknown"})
        payload["visitor_team_id"] = payload.pop("VISITOR_TEAM_ID")  
        payload["visitor_team_abbr"] = visitor_team_info["abbreviation"]
        payload["away_team"] = visitor_team_info["team_name"]
         
        return payload
    except Exception as e:
        logging.error(f"Error transforming team IDs: {e}")
        return None


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None
    

def get_game_status(game_date_str, status_id=None):
    current_date = datetime.today().date()
    if status_id is not None:
        return status_id != 1
    try:
        game_date = datetime.strptime(game_date_str, "%Y-%m-%d").date()
        return game_date < current_date 
    except ValueError:
        logging.error(f"Error trying to convert game date: {game_date_str}")
        return None


@functions_framework.cloud_event
def callback_upcoming_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        remove_fields(payload)
        payload["GAME_DATE"] = transform_game_date(payload["GAME_DATE"])
        payload["SEASON"] = transform_season(payload["SEASON"])
        game_status = get_game_status(payload["GAME_DATE"], payload["GAME_STATUS_ID"])
        payload["is_completed"] = game_status
        del payload["GAME_STATUS_ID"]
        payload = transform_team_id_to_abbr(payload)
        payload = {k.lower(): v for k, v in payload.items()}

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
        