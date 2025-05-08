from flask import Flask
import logging
import os
import time

from handlers.teams import get_teams
from handlers.games import get_games, get_games_week
from handlers.stats import get_team_metrics, get_team_season_stats, get_team_stats
from handlers.theodds_api import get_odds_week


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Env. variables defined in Terraform
# topic_teams = os.getenv("TOPIC_nba_teams")
# topic_games = os.getenv("TOPIC_nba_games")
# topic_games_week = os.getenv("TOPIC_nba_games_week")
# topic_metrics = os.getenv("TOPIC_team_metrics")
# topic_season_stats = os.getenv("TOPIC_team_season_stats")
# topic_stats = os.getenv("TOPIC_team_stats")
# topic_odds = os.getenv("TOPIC_odds_week")

# variables to use WITHOUT terraform
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
        time.sleep(5)
        get_games(topic_games)
        logging.info("NBA games sent to PubSub")
        time.sleep(5)
        get_games_week(topic_games_week)
        logging.info("NBA upcoming games sent to PubSub")
        time.sleep(5)
        get_team_metrics(topic_metrics)
        logging.info("NBA team metrics sent to PubSub")
        time.sleep(5)
        get_team_season_stats(topic_season_stats)
        logging.info("NBA season stats sent to PubSub")
        time.sleep(5)
        get_team_stats(topic_stats)
        logging.info("NBA team stats sent to PubSub")
        time.sleep(5)
        # get_odds_week(topic_odds)
        # logging.info("NBA betting odds sent to PubSub")
        return {"status": "success"}, 200
    except Exception as e:
        logging.error(f"Error in nba_odds_week: {str(e)}")
        return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
