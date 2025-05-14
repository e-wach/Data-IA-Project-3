from nba_api.stats.endpoints import leaguegamefinder
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING)

SEASONS = ['2022-23', '2023-24', '2024-25']
CUTOFF_DATE = "2025-05-11"

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

all_seasons_df = []

for season in SEASONS:
    gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00", season_nullable=season)
    games_df = gamefinder.get_data_frames()[0]

    games_df["GAME_DATE"] = games_df["GAME_DATE"].apply(transform_game_date)
    games_df[["HOME_TEAM", "AWAY_TEAM", "HOME_AWAY"]] = games_df["MATCHUP"].apply(
        lambda x: pd.Series(transform_matchup(x))
    )
    games_df["SEASON"] = season
    all_seasons_df.append(games_df)

# Concatenamos y filtramos por la fecha límite
final_df = pd.concat(all_seasons_df)
final_df = final_df[final_df["GAME_DATE"] <= CUTOFF_DATE]

# Exportamos a CSV
final_df.to_csv("years_22-25.csv", index=False)
