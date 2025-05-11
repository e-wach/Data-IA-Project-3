from flask import Flask, jsonify
import logging
import os
import time

from handlers.teams import get_teams
from handlers.games import get_games, get_games_week
from handlers.stats import get_stats
from handlers.theodds_api import get_odds_week


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Env. variables defined in Terraform
topic_teams = os.getenv("TOPIC_nba_teams", "nba_teams")
topic_games = os.getenv("TOPIC_nba_games", "nba_games")
topic_games_week = os.getenv("TOPIC_nba_games_week", "nba_games_week")
# topic_stats = os.getenv("TOPIC_games_stats", "games_stats")
topic_odds = os.getenv("TOPIC_odds_week", "odds_week")


@app.route("/setup/<string:type>", methods=["POST"])
def historical_data(type):
    try:
        if type == "teams":
            get_teams(topic_teams)
            logging.info("NBA teams sent to PubSub")
        elif type == "games":
            seasons = ["2022-23", "2023-24", "2024-25"]
            get_games(topic_games, seasons)
            logging.info("NBA historical games sent to PubSub")
        # elif type == "stats":
        #     seasons = ["2022-23", "2023-24", "2024-25"]
        #     get_stats(topic_stats, seasons)
        #     logging.info("NBA historical stats sent to PubSub")
        elif type == "upcomingGames":
            get_games_week(topic_games_week)
            logging.info("NBA upcoming games sent to PubSub")
        # elif type == "odds":
            # get_odds_week(topic_odds)
            # logging.info("NBA betting odds sent to PubSub")
        elif type == "all":
            get_teams(topic_teams)
            logging.info("NBA teams sent to PubSub")
            time.sleep(10)
            seasons = ["2022-23", "2023-24", "2024-25"]
            get_games(topic_games, seasons)
            logging.info("NBA historical games sent to PubSub")
            time.sleep(10)
            # seasons = ["2022-23", "2023-24", "2024-25"]
            # get_stats(topic_stats, seasons)
            # logging.info("NBA historical stats sent to PubSub")
            # time.sleep(10)
            get_games_week(topic_games_week)
            logging.info("NBA upcoming games sent to PubSub")
            time.sleep(10)
            # get_odds_week(topic_odds)
            # logging.info("NBA betting odds sent to PubSub")
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
            seasons = ["2024-25"]
            get_games(topic_games, seasons, fetch_all=False)
            logging.info("2024-25 NBA games sent to PubSub")
        elif type == "upcomingGames":
            get_games_week(topic_games_week)
            logging.info("NBA upcoming games sent to PubSub")
        # elif type == "stats": ######################## SOLO HASTA ABRIL 2025
        #     seasons = ["2024-25"]
        #     get_stats(topic_stats, seasons, fetch_all=False)
        #     logging.info("2024-25 NBA stats sent to PubSub")
        # elif type == "odds":
            # get_odds_week(topic_odds)
            # logging.info("NBA betting odds sent to PubSub")
        elif type == "all":
            seasons = ["2024-25"]
            get_games(topic_games, seasons)
            logging.info("2024-25 NBA games sent to PubSub")
            time.sleep(10)
            get_games_week(topic_games_week)
            logging.info("NBA upcoming games sent to PubSub")
            # seasons = ["2024-25"]
            # get_stats(topic_stats, seasons)
            # logging.info("2024-25 NBA stats sent to PubSub")
            # get_odds_week(topic_odds)
            # logging.info("NBA betting odds sent to PubSub")
        else:
            return jsonify({"error": "Invalid type provided."}), 400
        return {"status": "success", "message": f"{type} data sent to PubSub"}, 200
    except Exception as e:
        logging.error(f"Error fetching daily data for {type}: {str(e)}")
        return {"status": "error", "message": str(e)}, 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
