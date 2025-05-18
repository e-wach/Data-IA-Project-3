from flask import Flask, jsonify
import logging
import os
import time

from handlers.theodds_api import get_odds_week
from handlers.upcoming_games import get_upcoming_games
from handlers.games import latest_games, yesterday_games
from handlers.injured_players import get_injuries
from handlers.predictions import get_predictions

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Env. variables defined in Terraform
PROJECT_ID = os.getenv("PROJECT_ID", "default-project")
topic_games = os.getenv("TOPIC_nba_games", "default-topic")
topic_games_week = os.getenv("TOPIC_nba_games_week", "default-topic")
topic_odds = os.getenv("TOPIC_odds_week", "default-topic")
topic_injured = os.getenv("TOPIC_injured_players", "default-topic")
# Env. variables for Agent AI predictions endpoint
SQL_HOST = os.getenv("SQL_HOST", "default-host")
SQL_USER = os.getenv("SQL_USER", "default-user")
SQL_PASS = os.getenv("SQL_PASS", "password")
SQL_DB = os.getenv("SQL_DB", "default-db")
# API KEYS
API_KEY_ODDS = os.getenv('API_KEY_ODDS', 'default_key')
API_KEY_SD = os.getenv("API_KEY_SD", "default_key")


@app.route("/setup/<string:type>", methods=["POST"])
def historical_data(type):
    try:
        if type == "games":
            start_date_str = "2025-05-12"
            latest_games(topic_games, start_date_str, PROJECT_ID, API_KEY_SD)
        elif type == "upcomingGames":
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
        elif type == "odds":
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
        elif type == "injured":
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
        elif type == "all":
            start_date_str = "2025-05-12"
            latest_games(topic_games, start_date_str, PROJECT_ID, API_KEY_SD)
            time.sleep(5)
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
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
        elif type == "upcomingGames":
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
        elif type == "odds":
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
        elif type == "injured":
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
        elif type == "predictions":
            get_predictions(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
        elif type == "all":
            yesterday_games(topic_games, PROJECT_ID, API_KEY_SD)
            time.sleep(5)
            get_upcoming_games(topic_games_week, PROJECT_ID, API_KEY_SD)
            get_odds_week(topic_odds, PROJECT_ID, API_KEY_ODDS)
            get_injuries(topic_injured, PROJECT_ID, API_KEY_SD)
            get_predictions(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
        else:
            return jsonify({"error": "Invalid type provided."}), 400
        return {"status": "success", "message": f"{type} data sent to PubSub"}, 200
    except Exception as e:
        logging.error(f"Error fetching daily data for {type}: {str(e)}")
        return {"status": "error", "message": str(e)}, 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)


