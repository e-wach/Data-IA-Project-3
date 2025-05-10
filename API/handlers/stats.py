import json
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

from .publisher import publish_message


def get_stats(topic, seasons):
    team_ids = [team.get("id") for team in teams.get_teams()]
    try:
        for team in team_ids:
            gamelog = teamgamelog.TeamGameLog(season=seasons, team_id=team)
            data = gamelog.get_normalized_dict()["TeamGameLog"]
            for log in data:
                message = {
                    "Team_ID": log["Team_ID"],
                    "Game_ID": log["Game_ID"],
                    "GAME_DATE": log["GAME_DATE"],
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
                print(f"Published message to topic {topic}: {message}")
    except Exception as e:
        print(f"Error fetching stats: {str(e)}")    

