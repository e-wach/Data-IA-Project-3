from google.cloud import pubsub_v1
from flask import Flask
import json
import logging
import requests
import os

from handlers.teams import get_teams
from handlers.games import get_games, get_games_week
from handlers.stats import get_team_metrics, get_team_season_stats, get_team_stats
from handlers.theodds_api import get_odds_week


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

### DEFINIR TODOS LOS TOPICS EN VARIABLES DE ENTORNO (os.getenv())
topic_teams = "nba_teams"
topic_games = "nba_games"
topic_games_week = "nba_games_week"
topic_metrics = "team_metrics"
topic_season_stats = "team_season_stats"
topic_stats = "team_stats"
topic_odds = "odds_week"


@app.route("/fetchAll", methods=["POST"])
def fetch_all():
    try:
        get_teams(topic_teams)
        logging.info("NBA teams sent to PubSub")
        get_games(topic_games)
        logging.info("NBA games sent to PubSub")
        get_games_week(topic_games_week)
        logging.info("NBA upcoming games sent to PubSub")
        get_team_metrics(topic_metrics)
        logging.info("NBA team metrics sent to PubSub")
        get_team_season_stats(topic_season_stats)
        logging.info("NBA season stats sent to PubSub")
        get_team_stats(topic_stats)
        logging.info("NBA team stats sent to PubSub")
        get_odds_week(topic_odds)
        logging.info("NBA betting odds sent to PubSub")
        return {"status": "success"}, 200
    except Exception as e:
        logging.error(f"Error in nba_odds_week: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
