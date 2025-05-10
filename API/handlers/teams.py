import json
import logging
from nba_api.stats.static import teams

from publisher import publish_message


logging.basicConfig(level=logging.DEBUG)


def get_teams(topic):
    nba_teams = teams.get_teams()
    try:
        for team in nba_teams:
            message = json.dumps({
                "team_id": team.get("id"), 
                "team_name": team.get("full_name"), 
                "nickname": team.get("nickname"),
                "city": team.get("city"),
                "state": team.get("state"),
                "year_founded": team.get("year_founded")
            })
            publish_message(topic, message)
            logging.info(f"Published message to topic {topic}: {message}")
        return {"status": "ok", "message": "Teams published"}, 200
    except Exception as e:
        logging.error(f"Error publishing message: {e}")
        return {"status": "error", "message": str(e)}, 500