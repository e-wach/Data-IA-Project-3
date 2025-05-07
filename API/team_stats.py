from flask import Flask
from google.cloud import pubsub_v1
import logging
import json
import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamyearbyyearstats, teamestimatedmetrics, leaguedashteamstats
from nba_api.live.nba.endpoints import scoreboard

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

PROJECT_ID = "feisty-lamp-442712-m8"

def publish_message(topic, message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, message.encode("utf-8"))

# 1. teamyearbyyearstats
@app.route("/team_stats", methods=["POST"])
def get_team_stats():
    nba_teams = teams.get_teams()
    topic = "nba_team_stats"
    try:
        for team in nba_teams:
            team_id = team["id"]
            team_name = team["full_name"]
            response = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id)
            records = response.get_normalized_dict()["TeamStats"]
            for record in records:
                record["team_name"] = team_name
                message = json.dumps(record)
                publish_message(topic, message)
                logging.info(f"Published to {topic}: {message}")
            time.sleep(1)
        return {"status": "ok", "message": "Team stats published"}, 200
    except Exception as e:
        logging.error(f"Error publishing team stats: {e}")
        return {"status": "error", "message": str(e)}, 500

# 2. teamestimatedmetrics
@app.route("/team_metrics", methods=["POST"])
def get_team_metrics():
    topic = "nba_team_metrics"
    try:
        response = teamestimatedmetrics.TeamEstimatedMetrics()
        records = response.get_normalized_dict()["TeamEstimatedMetrics"]
        for record in records:
            message = json.dumps(record)
            publish_message(topic, message)
            logging.info(f"Published to {topic}: {message}")
        return {"status": "ok", "message": "Team metrics published"}, 200
    except Exception as e:
        logging.error(f"Error publishing team metrics: {e}")
        return {"status": "error", "message": str(e)}, 500

# 3. leaguedashteamstats
@app.route("/team_season_stats", methods=["POST"])
def get_team_season_stats():
    topic = "nba_team_season_stats"
    try:
        response = leaguedashteamstats.LeagueDashTeamStats(season="2024-25")
        records = response.get_normalized_dict()["LeagueDashTeamStats"]
        for record in records:
            message = json.dumps(record)
            publish_message(topic, message)
            logging.info(f"Published to {topic}: {message}")
        return {"status": "ok", "message": "Team season stats published"}, 200
    except Exception as e:
        logging.error(f"Error publishing team season stats: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
    
