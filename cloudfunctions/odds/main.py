import base64
import functions_framework
import os
import logging
import json
import psycopg2


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
SQL_DB = os.getenv("DB_NAME", "nba_database")
SQL_USER = os.getenv("USER", "nba_user")
SQL_PASS =  os.getenv("SQL_PASS", "dataproject3")
SQL_HOST = os.getenv("SQL_HOST", "34.22.170.250")


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
        CREATE TABLE IF NOT EXISTS game_odds (
        id SERIAL PRIMARY KEY,
        game_id VARCHAR(255) NOT NULL,
        home_team VARCHAR(255),
        away_team VARCHAR(255),
        bookmakers JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_game_odds_game_id ON game_odds(game_id);
        CREATE INDEX IF NOT EXISTS idx_game_odds_bookmakers ON game_odds USING GIN (bookmakers);
        """
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        logging.info("Table game_odds created (if it didn't exist).")
    except Exception as e:
        logging.error(f"Error creating table: {e}")
        raise


def insert_postgres(payload):
    try:
        db_payload = payload.copy()
        if isinstance(db_payload["bookmakers"], (dict, list)):
            db_payload["bookmakers"] = json.dumps(db_payload["bookmakers"])
        with get_postgres_connection() as conn:
            with conn.cursor() as cursor:
                delete_query = """
                DELETE FROM nba_games_week 
                WHERE created_at < NOW() - INTERVAL '1 day';
                """
                cursor.execute(delete_query)
                insert_query = """
                INSERT INTO game_odds (game_id, home_team, away_team, bookmakers)
                VALUES (
                    %(game_id)s,
                    %(home_team)s,
                    %(away_team)s,
                    %(bookmakers)s::jsonb
                );
                """
                cursor.execute(insert_query, db_payload)
                conn.commit()
        logging.info("Data inserted into PostgreSQL.")
    except Exception as e:
        logging.error(f"Error inserting data PostgreSQL: {e}")
        raise

# NBA TEAMS
@functions_framework.cloud_event
def callback_odds(cloud_event):
    try:
        payload = json.loads(base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8'))
        insert_postgres(payload)
    except Exception as e:
        logging.error(f"Error trying to process NBA odds: {e}")
        raise
        