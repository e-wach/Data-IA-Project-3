import requests
import datetime
import logging
import json
import os

from .publisher import publish_message

logging.basicConfig(level=logging.DEBUG)

today = datetime.date.today()
dates = [today + datetime.timedelta(days=i) for i in range(7)]

API_KEY_SD = os.getenv("API_KEY", "default_key")

def get_upcoming_games(topic):
    today = datetime.date.today()
    dates = [today + datetime.timedelta(days=i) for i in range(7)]
    total_published = 0  # <--- Inicialización
    try:
        for date in dates:
            date_str = date.strftime("%Y-%m-%d")
            url = f"https://api.sportsdata.io/v3/nba/scores/json/ScoresBasic/{date_str}"
            headers = {
                "Ocp-Apim-Subscription-Key": API_KEY_SD
            }
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                games = response.json()
                for game in games:
                    game["GAME_DATE"] = date_str
                    message = json.dumps(game)
                    publish_message(topic, message)
                    logging.info(f"Published message to topic {topic}: {message}")
                    total_published += 1
            else:
                logging.error(f"Error fetching games for {date_str}: {response.status_code}")
    except Exception as e:
        logging.error(f"Error during the API request: {e}")
        return {"status": "error", "message": str(e)}, 500
    return {"status": "ok", "games_published": total_published}, 200
