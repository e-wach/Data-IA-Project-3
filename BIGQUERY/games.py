import os
import logging
import json
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import bigquery

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ID         = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
SUBSCRIPTION_NAME  = os.getenv("SUB_NBA_GAMES", "nba_games-sub")
DATASET_ID         = os.getenv("BQ_DATASET", "nba_dataset")
TABLE_ID           = os.getenv("BQ_TABLE", "nba_games")


subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
bq = bigquery.Client(project=PROJECT_ID)


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None


def transform_matchup(matchup):
    if "vs." in matchup:
        home_team, away_team = matchup.split(" vs.")
        return home_team.strip(), away_team.strip(), "home"
    elif "@" in matchup:
        away_team, home_team = matchup.split(" @")
        return home_team.strip(), away_team.strip(), "away"
    else:
        return matchup, matchup, None


def insert_into_bigquery(record):
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        errors = bq.insert_rows_json(table_ref, [record])
        if errors:
            logging.error(f"Errores al insertar en BigQuery: {errors}")
        else:
            logging.info("Inserción exitosa en BigQuery.")
    except Exception as e:
        logging.error(f"Error al insertar en BigQuery: {e}")


def callback(message):
    try:
        logging.info(f"Received message: {message.data.decode('utf-8')}")      
        payload = json.loads(message.data.decode('utf-8'))

        if "game_date" not in payload or "matchup" not in payload:
            logging.warning("Faltan campos obligatorios.")
            message.nack()
            return
        payload["game_date"] = transform_game_date(payload["game_date"])
        home, away, m_type = transform_matchup(payload["matchup"])
        payload["home_team"] = home
        payload["away_team"] = away
        payload["matchup_type"] = m_type
        insert_into_bigquery(payload)
        message.ack()
        logging.info("Mensaje procesado correctamente.")
    except Exception as e:
        logging.error(f"Error procesando el mensaje: {e}")
        message.nack()


def listen_for_messages():
    streaming_pull_future = subscriber.subscribe(sub_path, callback=callback)
    try:
        streaming_pull_future.result()
    except Exception as e:
        logging.error(f"Error while listening: {e}")
        streaming_pull_future.cancel()


if __name__ == "__main__":
    listen_for_messages()
