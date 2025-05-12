import logging
import json
import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamyearbyyearstats, teamestimatedmetrics, leaguedashteamstats

from .publisher import publish_message


logging.basicConfig(level=logging.INFO)


# 1. teamyearbyyearstats
def get_team_stats(topic):
    nba_teams = teams.get_teams()
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
def get_team_metrics(topic):
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
def get_team_season_stats(topic):
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

