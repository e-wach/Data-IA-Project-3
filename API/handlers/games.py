import json
import logging
import time
from datetime import datetime, timedelta
from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2

from .publisher import publish_message

logging.basicConfig(level=logging.DEBUG)


# NBA completed games
def get_games(topic, seasons, fetch_all=True):
    all_games = []
    try:
        for season in seasons:
            gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
            games = gamefinder.get_normalized_dict()["LeagueGameFinderResults"]
            if not fetch_all: 
                yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
                yesterday_str = yesterday.strftime('%Y-%m-%d')
            for game in games:
                game_date = game["game_date"]
                if fetch_all or game_date >= yesterday_str:
                    game_data = {
                        "season_id": game["SEASON_ID"],
                        "season": season,
                        "team_id": game["TEAM_ID"],
                        "team_abbr": game["TEAM_ABBREVIATION"],
                        "team_name": game["TEAM_NAME"],
                        "game_id": game["GAME_ID"],
                        "game_date": game_date,
                        "matchup": game["MATCHUP"],
                        "win_loss": game["WL"],
                        "points": game["PTS"],
                        "fg_pct": game["FG_PCT"],
                        "three_pt_pct": game["FG3_PCT"],
                        "ft_pct": game["FT_PCT"],
                        "reb": game["REB"],
                        "ast": game["AST"],
                        "tov": game["TOV"],
                        "plus_minus": game["PLUS_MINUS"]
                    }
                    all_games.append(game_data)
                    try:
                        message = json.dumps(game_data)
                        publish_message(topic, message)
                        logging.info(f"Published message to topic {topic}: {message}")
                    except Exception as e:
                        logging.error(f"Error publishing message for game {game['GAME_ID']}: {e}")
    except Exception as e:
            logging.error(f"Error fetching games for season {season}: {e}")
    time.sleep(10)


# NBA upcoming games of the week 
########### TEAMS EN CÓDIGO / HORA EN STRING (ET)
def get_games_week(topic):
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    games_this_week = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        try:
            scoreboard = scoreboardv2.ScoreboardV2(game_date=date_str)
            games = scoreboard.get_data_frames()[0]     
            games_list = games.to_dict(orient='records')
            for game in games_list:
                game["GAME_DATE"] = date_str
                games_this_week.append(game)
                message = json.dumps(game)
                publish_message(topic, message)
                logging.info(f"Published message to topic {topic}: {message}")
        except Exception as e:
            logging.error(f"Error al obtener juegos del {date_str}: {e}")
    return {"status": "ok", "games_published": len(games_this_week)}, 200
