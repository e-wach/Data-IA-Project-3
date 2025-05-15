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
        CREATE TABLE IF NOT EXISTS injured_players (
    player_id INTEGER,
    team_id INTEGER,
    team_abbr VARCHAR(10),
    status VARCHAR(10),
    first_name VARCHAR(50),
    first_last VARCHAR(50),
    injury_start_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        logging.info("Table injured_players created (if it didn't exist).")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        raise


def insert_postgres(payload):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        delete_query = """
        DELETE FROM injured_players 
        WHERE created_at < NOW() - INTERVAL '1 day';
        """
        cursor.execute(delete_query)
        insert_query = """
        INSERT INTO injured_players (
        player_id, team_id, team_abbr, status, first_name, last_name, injury_start_date)
        VALUES (%(player_id)s, %(team_id)s, %(team_abbr)s, %(status)s,
        %(first_name)s, %(last_name)s, %(injury_start_date)s
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


def transform_date(injured_date):
    try:
        return datetime.strptime(injured_date, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid date format: {injured_date}")
        return None


def transform_team_id(payload):
    try:
        with open("combined_teams.json", 'r') as f:
            nba_teams = json.load(f)
            teams_dict = {team["team_id_sd"]: team for team in nba_teams}

        team_sd_id = payload.get("team_id")
        team_info = teams_dict.get(team_sd_id)

        if team_info:
            payload["team_id"] = team_info.get("team_id_nba", "Unknown")
            payload["team_abbr"] = team_info.get("abbreviation", "Unknown")
        else:
            payload["team_id"] = "Unknown"
            payload["team_abbr"] = "Unknown"

        return payload

    except Exception as e:
        logging.error(f"Error transforming team info: {e}")
        return payload


@functions_framework.cloud_event
def callback_upcoming_games(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        payload["injury_start_date"] = transform_date(payload["injury_start_date"])
        payload = transform_team_id(payload)
        insert_postgres(payload)
    except Exception as e:
        logging.error(f"Error trying to process NBA upcoming teams: {e}")
        raise

