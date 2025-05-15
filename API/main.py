from flask import Flask, jsonify
import logging
import os
import time

from handlers.theodds_api import get_odds_week
from handlers.upcoming_games import get_upcoming_games
from handlers.games import latest_games, yesterday_games
from handlers.injured_players import get_injuries

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Env. variables defined in Terraform
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "data-ia-project-3")
topic_teams = os.getenv("TOPIC_nba_teams", "nba_teams")
topic_games = os.getenv("TOPIC_nba_games", "nba_games")
topic_games_week = os.getenv("TOPIC_nba_games_week", "nba_games_week")
topic_odds = os.getenv("TOPIC_odds_week", "odds_week")
topic_injured = os.getenv("TOPIC_injured_players", "injured_players")
# Env. variables for Agent AI predictions endpoint
SQL_HOST = os.getenv("SQL_HOST", "DEFAULT_HOST")
SQL_USER = os.getenv("SQL_USER", "nba_user")
SQL_PASS = os.getenv("SQL_PASS", "dataproject3")
SQL_DB = os.getenv("SQL_DB", "nba_database")
# API KEYS
API_KEY_ODDS = os.getenv('API_KEY_ODDS', 'default_key')
API_KEY_SD = os.getenv("API_KEY_SD", "default_key")


@app.route("/setup/<string:type>", methods=["POST"])
def historical_data(type):
    try:
        if type == "games":
            start_date_str = "2025-05-12"
            latest_games(topic_games, start_date_str, PROJECT_ID, API_KEY_SD)
            logging.info("NBA lastest games sent to PubSub")
        elif type == "upcomingGames":
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            logging.info("NBA upcoming games sent to PubSub")
        elif type == "odds":
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            logging.info("NBA betting odds sent to PubSub")
        elif type == "injured":
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
            logging.info("NBA injured players sent to PubSub")
        elif type == "all":
            start_date_str = "2025-05-12"
            latest_games(topic_games, start_date_str, PROJECT_ID, API_KEY_SD)
            logging.info("NBA lastest games sent to PubSub")
            time.sleep(5)
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            logging.info("NBA upcoming games sent to PubSub")
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            logging.info("NBA betting odds sent to PubSub")
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
            logging.info("NBA injured players sent to PubSub")
        else:
            return jsonify({"error": "Invalid type provided."}), 400
        return {"status": "success", "message": f"{type} data sent to PubSub"}, 200
    except Exception as e:
        logging.error(f"Error fetching historical data for {type}: {str(e)}")
        return {"status": "error", "message": str(e)}, 500
    

@app.route("/daily/<string:type>", methods=["POST"])
def daily_data(type):
    try:
        if type == "games":
            yesterday_games(topic_games, PROJECT_ID, API_KEY_SD)
            logging.info("2024-25 NBA games sent to PubSub")
        elif type == "upcomingGames":
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            logging.info("NBA upcoming games sent to PubSub")
        elif type == "odds":
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            logging.info("NBA betting odds sent to PubSub")
        elif type == "injured":
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
            logging.info("NBA injured players sent to PubSub")
        elif type == "all":
            yesterday_games(topic_games, PROJECT_ID, API_KEY_SD)
            logging.info("2024-25 NBA games sent to PubSub")
            time.sleep(5)
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            logging.info("NBA upcoming games sent to PubSub")
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            logging.info("NBA betting odds sent to PubSub")
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
            logging.info("NBA injured players sent to PubSub")
        else:
            return jsonify({"error": "Invalid type provided."}), 400
        return {"status": "success", "message": f"{type} data sent to PubSub"}, 200
    except Exception as e:
        logging.error(f"Error fetching daily data for {type}: {str(e)}")
        return {"status": "error", "message": str(e)}, 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)


