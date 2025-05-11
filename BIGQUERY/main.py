import os
import logging
import json
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import bigquery

from handlers.transform_games import transform_game_date, transform_matchup
from utils.load_bq import insert_into_bigquery
from utils.pubsub import listen_for_messages


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ID         = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
SUBSCRIPTION_NAME  = os.getenv("SUB_NBA_GAMES", "nba_games-sub")
DATASET_ID         = os.getenv("BQ_DATASET", "nba_dataset")
TABLE_ID           = os.getenv("BQ_TABLE", "nba_games")


subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)
bq = bigquery.Client(project=PROJECT_ID)

# NBA GAMES (completed games)
def callback_games(message):
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
        insert_into_bigquery(bq, payload, PROJECT_ID, DATASET_ID, TABLE_ID)
        message.ack()
        logging.info("Mensaje procesado correctamente.")
    except Exception as e:
        logging.error(f"Error procesando el mensaje: {e}")
        message.nack()



if __name__ == "__main__":
    listen_for_messages(callback_games, subscription_name=SUBSCRIPTION_NAME, project_id=PROJECT_ID)
