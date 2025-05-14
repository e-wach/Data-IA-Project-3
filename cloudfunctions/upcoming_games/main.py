import base64
import functions_framework
from datetime import datetime
import os
import logging
import json
import psycopg2


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
SQL_DB = os.getenv("DB_NAME", "nba_database")
SQL_USER = os.getenv("USER", "nba_user")
SQL_PASS =  os.getenv("SQL_PASS", "dataproject3")
SQL_HOST = os.getenv("SQL_HOST", "default_host")


def get_postgres_connection():
    conn = psycopg2.connect(
        dbname=SQL_DB,
        user=SQL_USER,
        password=SQL_PASS,
        host=SQL_HOST,
        port="5432"
    )
    create_table_if_not_exists(conn)
    return conn

def create_table_if_not_exists(conn):
    try:
        cursor = conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS nba_games_week (
    GameID INTEGER PRIMARY KEY,
    Season VARCHAR(10),
    SeasonType INTEGER,
    Status VARCHAR(50),
    GAME_DATE DATE,
    DateTime VARCHAR(10),
    HomeTeamID INTEGER,
    home_team_abbr VARCHAR(10),
    home_team_id_nba BIGINT,
    AwayTeamID INTEGER,
    away_team_abbr VARCHAR(10),
    away_team_id_nba BIGINT,
    AwayTeamScore INTEGER,
    HomeTeamScore INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        logging.info("Table nba_games_week created (if it didn't exist).")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        raise


def insert_postgres(payload):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        delete_query = """
        DELETE FROM nba_games_week 
        WHERE created_at < NOW() - INTERVAL '1 day';
        """
        cursor.execute(delete_query)
        insert_query = """
        INSERT INTO nba_games_week (
        GameID, Season, SeasonType, Status, GAME_DATE, DateTime, 
        home_team_id_nba,HomeTeamID, home_team_abbr, away_team_id_nba, 
        AwayTeamID, away_team_abbr,AwayTeamScore, HomeTeamScore)
        VALUES (%(GameID)s, %(Season)s, %(SeasonType)s, %(Status)s,
        %(GAME_DATE)s, %(DateTime)s, %(home_team_id_nba)s, 
        %(HomeTeamID)s, %(home_team_abbr)s, %(away_team_id_nba)s,
        %(AwayTeamID)s, %(away_team_abbr)s, %(AwayTeamScore)s, %(HomeTeamScore)s
        );
        """
        cursor.execute(insert_query, payload)
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data inserted into PostgreSQL.")
    except Exception as e:
        logging.error(f"Error inserting data PostgreSQL: {e}")
        raise



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
        payload["home_team_id_nba"] = home_team_info["team_id_nba"]
        visitor_team_info = nba_teams_dict.get(payload["AwayTeamID"], {"abbreviation": "Unknown", "team_name": "Unknown", "team_id_nba": "Unknown", "team_id_sd": "Unknown", "city": "Unknown", "nickname": "Unknown"})
        payload["away_team_id_nba"] = visitor_team_info["team_id_nba"]
        payload["away_team_abbr"] = visitor_team_info["abbreviation"]
        del payload["AwayTeam"]
        payload["away_team_nickname"] = visitor_team_info["nickname"]
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
        insert_postgres(payload)
    except Exception as e:
        logging.error(f"Error trying to process NBA upcoming teams: {e}")
        raise
        