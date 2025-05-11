import os
import logging
import json
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import bigquery

from utils.load_bq import insert_into_bigquery
from utils.pubsub import listen_for_messages

from handlers.transform_games import transform_game_date, transform_matchup, get_game_status
from handlers.transform_games_week import remove_fields, transform_season, transform_team_id_to_abbr
# from handlers.get_teams import callback_teams, teams_dict



logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "original-list-459014-b6")
# NBA_TEAMS_SUB = os.getenv("NBA_TEAMS_SUB", "nba_teams-sub")
NBA_GAMES_SUB  = os.getenv("NBA_GAMES_SUB", "nba_games-sub")
NBA_GAMES_WEEK_SUB = os.getenv("NBA_GAMES_WEEK_SUB","nba_games_week-sub")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_GAMES_TABLE = os.getenv("NBA_GAMES_TABLE", "nba_games")
NBA_GAMES_WEEK_TABLE = os.getenv("NBA_GAMES_WEEK_TABLE", "nba_games_week")


subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path(PROJECT_ID, NBA_GAMES_SUB)
bq = bigquery.Client(project=PROJECT_ID)


# NBA GAMES (completed games)
def callback_games(message):
    try:
        logging.info(f"Received message: {message.data.decode('utf-8')}")      
        payload = json.loads(message.data.decode('utf-8'))
        logging.info(f"Payload: {payload}")
        if "game_date" not in payload or "matchup" not in payload:
            logging.warning("Missing fields.")
            message.nack()
            return
        payload["game_date"] = transform_game_date(payload["game_date"])
        home, away, m_type = transform_matchup(payload["matchup"])
        payload["home_team"] = home
        payload["away_team"] = away
        payload["matchup_type"] = m_type
        game_status = get_game_status(payload["game_date"])
        payload["is_completed"] = game_status
        insert_into_bigquery(bq, payload, PROJECT_ID, DATASET_ID, NBA_GAMES_TABLE)
        message.ack()
        logging.info("Message processed sucessfully.")
    except Exception as e:
        logging.error(f"Error trying to process message: {e}")
        message.nack()

# NBA GAMES (next 7 days)
def callback_upcoming_games(message):
    try:
        payload = json.loads(message.data.decode('utf-8'))
        remove_fields(payload)
        payload["GAME_DATE"] = transform_game_date(payload["GAME_DATE"])
        payload["SEASON"] = transform_season(payload["SEASON"])
        game_status = get_game_status(payload["GAME_DATE"], payload["GAME_STATUS_ID"])
        payload["is_completed"] = game_status
        del payload["GAME_STATUS_ID"]
        payload = transform_team_id_to_abbr(payload)
        payload = {k.lower(): v for k, v in payload.items()}
        logging.info(f"Upcoming game transformed: {payload}")
        insert_into_bigquery(bq, payload, PROJECT_ID, DATASET_ID, NBA_GAMES_WEEK_TABLE)

        message.ack()
        logging.info(f"Message processed sucessfully: {payload}.")
    except Exception as e:
        logging.error(f"Error trying to process message: {e}")
        message.nack()




if __name__ == "__main__":
    # listen_for_messages(callback_games, subscription_name=NBA_GAMES_SUB, project_id=PROJECT_ID)
    listen_for_messages(callback_upcoming_games, subscription_name=NBA_GAMES_WEEK_SUB, project_id=PROJECT_ID)
