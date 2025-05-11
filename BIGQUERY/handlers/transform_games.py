from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None


def transform_matchup(matchup):
    if "vs." in matchup:
        home_team, away_team = matchup.split(" vs.")
        return home_team.strip(), away_team.strip(), "home"
    elif "@" in matchup:
        away_team, home_team = matchup.split(" @")
        return home_team.strip(), away_team.strip(), "away"
    else:
        return matchup, matchup, None
    

def get_game_status(game_date_str, status_id=None):
    current_date = datetime.today().date()
    if status_id is not None:
        return status_id != 1
    try:
        game_date = datetime.strptime(game_date_str, "%Y-%m-%d").date()
        return game_date < current_date 
    except ValueError:
        logging.error(f"Error trying to convert game date: {game_date_str}")
        return None
