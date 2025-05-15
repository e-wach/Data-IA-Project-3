import requests
import datetime
import logging
import json
from datetime import timedelta, datetime

from .publisher import publish_message

logging.basicConfig(level=logging.DEBUG)


def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


def process_publish(topic, date_str, PROJECT_ID, API_KEY_SD):
    url = f"https://api.sportsdata.io/v3/nba/scores/json/TeamGameStatsByDate/{date_str}"
    url_add = f"https://api.sportsdata.io/v3/nba/scores/json/GamesByDate/{date_str}"
    headers = {
            "Ocp-Apim-Subscription-Key": API_KEY_SD
            }
    response = requests.get(url, headers=headers)
    response_add = requests.get(url_add, headers=headers)
    
    if response.status_code == 200 and response_add.status_code == 200:
        data = response.json()
        extra_data = response_add.json()
        extra_data_map = {g["GameID"]: g for g in extra_data}
    if not data:
        logging.info("No data found for the given date.")
        return
    for game in data:
        extra = extra_data_map.get(game.get("GameID"), {})
        away_team_score = extra.get("AwayTeamScore", 0)
        home_team_score = extra.get("HomeTeamScore", 0)
        if game.get("HomeOrAway") == "HOME":
            points = home_team_score
        else:
            points = away_team_score
        game_data = {
                "team_id_sd": game.get("TeamID", 0),
                "season": game.get("Season", 0),
                "team_name": game.get("Name", ""),
                "team_abbr": game.get("Team", ""),
                "wins": game.get("Wins", 0),
                "losses": game.get("Losses", 0),
                "points": points,
                "possessions": game.get("Possessions", 0),
                "game_id": game.get("GameID", 0),
                "away_team_id_sd": game.get("OpponentID", 0),
                "away_team": game.get("Opponent", ""),
                "game_date": game.get("Day", ""),
                "date_time": game.get("DateTime", ""),
                "home_away": game.get("HomeOrAway", ""),
                "fantasy_points": game.get("FantasyPoints", 0),
                "field_goals_made": game.get("FieldGoalsMade", 0),
                "field_goals_attempted": game.get("FieldGoalsAttempted", 0),
                "field_goals_percentage": game.get("FieldGoalsPercentage", 0),
                "effective_field_goals_percentage": game.get("EffectiveFieldGoalsPercentage", 0),
                "two_pointers_made": game.get("TwoPointersMade", 0),
                "two_pointers_attempted": game.get("TwoPointersAttempted", 0),
                "two_pointers_percentage": game.get("TwoPointersPercentage", 0),
                "three_pointers_made": game.get("ThreePointersMade", 0),
                "three_pointers_attempted": game.get("ThreePointersAttempted", 0),
                "three_pointers_percentage": game.get("ThreePointersPercentage", 0),
                "free_throws_made": game.get("FreeThrowsMade", 0),
                "free_throws_attempted": game.get("FreeThrowsAttempted", 0),
                "free_throws_percentage": game.get("FreeThrowsPercentage", 0),
                "offensive_rebounds": game.get("OffensiveRebounds", 0),
                "defensive_rebounds": game.get("DefensiveRebounds", 0),
                "rebounds": game.get("Rebounds", 0),
                "offensive_rebounds_percentage": game.get("OffensiveReboundsPercentage", None),
                "defensive_rebounds_percentage": game.get("DefensiveReboundsPercentage", None),
                "total_rebounds_percentage": game.get("TotalReboundsPercentage", None),
                "assists": game.get("Assists", 0),
                "steals": game.get("Steals", 0),
                "blocked_shots": game.get("BlockedShots", 0),
                "turnovers": game.get("Turnovers", 0),
                "personal_fouls": game.get("PersonalFouls", 0),
                "true_shooting_attempts": game.get("TrueShootingAttempts", 0),
                "true_shooting_percentage": game.get("TrueShootingPercentage", 0),
                "player_efficiency_rating": game.get("PlayerEfficiencyRating", None),
                "assists_percentage": game.get("AssistsPercentage", None),
                "steals_percentage": game.get("StealsPercentage", None),
                "blocks_percentage": game.get("BlocksPercentage", None),
                "turnovers_percentage": game.get("TurnOversPercentage", None),
                "usage_rate_percentage": game.get("UsageRatePercentage", None),
                "fantasy_points_fanduel": game.get("FantasyPointsFanDuel", 0),
                "fantasy_points_draftkings": game.get("FantasyPointsDraftKings", 0),
                "fantasy_points_yahoo": game.get("FantasyPointsYahoo", 0),
                "plus_minus": game.get("PlusMinus", 0),
                "double_doubles": game.get("DoubleDoubles", 0),
                "triple_doubles": game.get("TripleDoubles", 0),
                "fantasy_points_fantasydraft": game.get("FantasyPointsFantasyDraft", 0)            
                }
        if game_data:
            try:
                message = json.dumps(game_data)
                publish_message(topic, message, PROJECT_ID)
                logging.info(f"Published message to topic {topic}: {message}")
            except Exception as e:
                logging.error(f"Error publishing message for game {game.get('GameID')}: {e}")
        else:
            logging.warning(f"Invalid data for game {game.get('GameID')}, skipping.")
    else:
        logging.error(f"Error calling API {url}: {response.status_code}")


# API call for games from 12/05/2025 to today (yesterday's last game)
def latest_games(topic, start_date_str, PROJECT_ID, API_KEY_SD):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.utcnow()
    for single_date in daterange(start_date, end_date):
        date_str = single_date.strftime("%Y-%m-%d")
        logging.info(f"Llamando API para: {date_str}")
        process_publish(topic, date_str, PROJECT_ID, API_KEY_SD)

# API call to update BigQuery games table with most recent games
def yesterday_games(topic, PROJECT_ID, API_KEY_SD):
    yesterday = datetime.utcnow() - timedelta(1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    logging.info(f"Llamando API para: {yesterday_str}")
    process_publish(topic, yesterday_str, PROJECT_ID, API_KEY_SD)


