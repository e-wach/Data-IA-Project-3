from nba_api.stats.endpoints import leaguegamefinder
from datetime import datetime
import logging
import json
import pandas as pd

logging.basicConfig(level=logging.WARNING)

gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00", season_nullable='2022-23')
games_df = gamefinder.get_data_frames()[0]

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

games_df["GAME_DATE"] = games_df["GAME_DATE"].apply(transform_game_date)
games_df[["HOME_TEAM", "AWAY_TEAM", "HOME_AWAY"]] = games_df["MATCHUP"].apply(
    lambda x: pd.Series(transform_matchup(x))
)

games_json = games_df.to_dict(orient='records')

with open("games_2022_23.json", "w") as f:
    json.dump(games_json, f, indent=4)
