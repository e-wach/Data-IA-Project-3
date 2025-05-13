import requests
import datetime
import logging
import json
import os
from datetime import timedelta, datetime

from .publisher import publish_message

logging.basicConfig(level=logging.DEBUG)


API_KEY_SD = os.getenv("API_KEY_SD", "default_key")


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


def process_publish(topic, date_str):
    url = f"https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsByDate/{date_str}"
    headers = {
            "Ocp-Apim-Subscription-Key": API_KEY_SD
            }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if not data:
            logging.info("No dara found for the given date.")
            return
        for game in data:
            game_data = { ################ CAMBIAR LAS KEY PARA QUE COINCIDA CON EL HISTÓRICO
                "TeamID": game.get("TeamID", 0),
                # "StatID": game.get("StatID", 0),
                # "SeasonType": game.get("SeasonType", 0),
                "season": game.get("Season", 0),
                "team_name": game.get("Name", ""),
                "team_abbr": game.get("Team", ""),
                "Wins": game.get("Wins", 0), ### cambiar a WL = L O W
                "Losses": game.get("Losses", 0),
                "Possessions": game.get("Possessions", 0),
                # "GlobalTeamID": game.get("GlobalTeamID", 0),
                "game_id": game.get("GameID", 0),
                "OpponentID": game.get("OpponentID", 0),
                "away_team": game.get("Opponent", ""),
                "Day": game.get("Day", ""),
                "DateTime": game.get("DateTime", ""),
                "HomeOrAway": game.get("HomeOrAway", ""),
                # "IsGameOver": game.get("IsGameOver", False),
                "GlobalGameID": game.get("GlobalGameID", 0),
                "GlobalOpponentID": game.get("GlobalOpponentID", 0),
                # "Updated": game.get("Updated", ""),
                "Games": game.get("Games", 0),
                "FantasyPoints": game.get("FantasyPoints", 0),
                "Minutes": game.get("Minutes", 0),
                "Seconds": game.get("Seconds", 0),
                "FieldGoalsMade": game.get("FieldGoalsMade", 0),
                "FieldGoalsAttempted": game.get("FieldGoalsAttempted", 0),
                "FieldGoalsPercentage": game.get("FieldGoalsPercentage", 0),
                "EffectiveFieldGoalsPercentage": game.get("EffectiveFieldGoalsPercentage", 0),
                "TwoPointersMade": game.get("TwoPointersMade", 0),
                "TwoPointersAttempted": game.get("TwoPointersAttempted", 0),
                "TwoPointersPercentage": game.get("TwoPointersPercentage", 0),
                "ThreePointersMade": game.get("ThreePointersMade", 0),
                "ThreePointersAttempted": game.get("ThreePointersAttempted", 0),
                "ThreePointersPercentage": game.get("ThreePointersPercentage", 0),
                "FreeThrowsMade": game.get("FreeThrowsMade", 0),
                "FreeThrowsAttempted": game.get("FreeThrowsAttempted", 0),
                "FreeThrowsPercentage": game.get("FreeThrowsPercentage", 0),
                "OffensiveRebounds": game.get("OffensiveRebounds", 0),
                "DefensiveRebounds": game.get("DefensiveRebounds", 0),
                "Rebounds": game.get("Rebounds", 0),
                "OffensiveReboundsPercentage": game.get("OffensiveReboundsPercentage", None),
                "DefensiveReboundsPercentage": game.get("DefensiveReboundsPercentage", None),
                "TotalReboundsPercentage": game.get("TotalReboundsPercentage", None),
                "Assists": game.get("Assists", 0),
                "Steals": game.get("Steals", 0),
                "BlockedShots": game.get("BlockedShots", 0),
                "Turnovers": game.get("Turnovers", 0),
                "PersonalFouls": game.get("PersonalFouls", 0),
                "Points": game.get("Points", 0),
                "TrueShootingAttempts": game.get("TrueShootingAttempts", 0),
                "TrueShootingPercentage": game.get("TrueShootingPercentage", 0),
                "PlayerEfficiencyRating": game.get("PlayerEfficiencyRating", None),
                "AssistsPercentage": game.get("AssistsPercentage", None),
                "StealsPercentage": game.get("StealsPercentage", None),
                "BlocksPercentage": game.get("BlocksPercentage", None),
                "TurnOversPercentage": game.get("TurnOversPercentage", None),
                "UsageRatePercentage": game.get("UsageRatePercentage", None),
                "FantasyPointsFanDuel": game.get("FantasyPointsFanDuel", 0),
                "FantasyPointsDraftKings": game.get("FantasyPointsDraftKings", 0),
                "FantasyPointsYahoo": game.get("FantasyPointsYahoo", 0),
                "PlusMinus": game.get("PlusMinus", 0),
                "DoubleDoubles": game.get("DoubleDoubles", 0),
                "TripleDoubles": game.get("TripleDoubles", 0),
                "FantasyPointsFantasyDraft": game.get("FantasyPointsFantasyDraft", 0),
                "IsClosed": game.get("IsClosed", False),
                "LineupConfirmed": game.get("LineupConfirmed", None),
                "LineupStatus": game.get("LineupStatus", "")
}
            if game_data:
                try:
                    message = json.dumps(game_data)
                    publish_message(topic, message)
                    logging.info(f"Published message to topic {topic}: {message}")
                except Exception as e:
                    logging.error(f"Error publishing message for game {game.get('GameID')}: {e}")
            else:
                logging.warning(f"Invalid data for game {game.get('GameID')}, skipping.")
    else:
        logging.error(f"Error calling API {url}: {response.status_code}")


# API call for games from 12/05/2025 to today (yesterday's last game)
def latest_games(topic, start_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.utcnow()
    for single_date in daterange(start_date, end_date):
        date_str = single_date.strftime("%Y-%m-%d")
        logging.info(f"Llamando API para: {date_str}")
        process_publish(topic, date_str)

# API call to update BigQuery games table with most recent games
def yesterday_games(topic):
    yesterday = datetime.utcnow() - timedelta(1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    logging.info(f"Llamando API para: {yesterday_str}")
    process_publish(topic, yesterday_str)


