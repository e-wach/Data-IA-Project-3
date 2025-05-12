import json
import logging
import time
from datetime import datetime, timedelta
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

from .publisher import publish_message


def get_stats(topic, seasons, fetch_all=True):
    team_ids = [team.get("id") for team in teams.get_teams()]
    yesterday = datetime.now() - timedelta(days=1)
    try:
        for team in team_ids:
            gamelog = teamgamelog.TeamGameLog(season=seasons, team_id=team)
            data = gamelog.get_normalized_dict()["TeamGameLog"]
            count = 0
            for log in data:
                game_date_str = log.get("GAME_DATE", "")
                try:
                    game_date = datetime.strptime(game_date_str, "%b %d, %Y")
                except ValueError:
                    logging.warning(f"Skipping game with invalid date format: {game_date_str}")
                    continue
                if fetch_all or game_date.date() >= yesterday.date():
                    message = {
                        "Team_ID": log["Team_ID"],
                        "Game_ID": log["Game_ID"],
                        "GAME_DATE": game_date_str,
                        "MATCHUP": log["MATCHUP"],
                        "WL": log["WL"],
                        "W": log["W"],
                        "L": log["L"],
                        "W_PCT": log["W_PCT"],
                        "MIN": log["MIN"],
                        "FGM": log["FGM"],
                        "FGA": log["FGA"],
                        "FG_PCT": log["FG_PCT"],
                        "FG3M": log["FG3M"],
                        "FG3A": log["FG3A"],
                        "FG3_PCT": log["FG3_PCT"],
                        "FTM": log["FTM"],
                        "FTA": log["FTA"],
                        "FT_PCT": log["FT_PCT"],
                        "OREB": log["OREB"],
                        "DREB": log["DREB"],
                        "REB": log["REB"],
                        "AST": log["AST"],
                        "STL": log["STL"],
                        "BLK": log["BLK"],
                        "TOV": log["TOV"],
                        "PF": log["PF"],
                        "PTS": log["PTS"]
                    }            
                    message_json = json.dumps(message)
                    publish_message(topic, message_json)
                    logging.info(f"Published message to topic {topic}: {message}")
                    count += 1
            if count == 0:
                if fetch_all:
                    logging.info(f"No games found for team {team} in season {seasons}.")
                else:
                    logging.info(f"No games found for team {team} from {yesterday.date()} onward.")
            time.sleep(5)
    except Exception as e:
        logging.error(f"Error fetching stats: {str(e)}")
