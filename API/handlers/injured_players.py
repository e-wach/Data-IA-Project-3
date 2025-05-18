import requests
import datetime
import logging
import json

from .publisher import publish_message

logging.basicConfig(level=logging.DEBUG)

def get_injuries(topic, PROJECT_ID, API_KEY_SD):
    try:
        url = f"https://api.sportsdata.io/v3/nba/projections/json/InjuredPlayers"
        headers = {
            "Ocp-Apim-Subscription-Key": API_KEY_SD
            }
        response = requests.get(url, headers=headers)
        injuries = response.json()
        if response.status_code == 200:
            for player in injuries:
                player_data = {
                    "player_id": player.get("PlayerID", 0),
                    "team_id": player.get("TeamID", 0),
                    "team_abbr": player.get("Team", 0),
                    "status": player.get("Status", 0),
                    "first_name": player.get("FirstName", 0),
                    "last_name": player.get("LastName", 0),
                    "injury_start_date": player.get("InjuryStartDate", 0)
                }
                message = json.dumps(player_data)
                logging.info(f"message sent to pubsub: {message}")
                publish_message(topic, message, PROJECT_ID)
                logging.info(f"Sent to {topic}")
        else:
            logging.error(f"Error fetching injured players: {response.status_code}")
    except Exception as e:
        logging.error(f"Error during the API request for injured players: {e}")
            