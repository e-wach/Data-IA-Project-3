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
    yesterday = datetime.now() - timedelta(days=1)
    for season in seasons:
        try:
            gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00",season_nullable=season)
            games = gamefinder.get_normalized_dict()["LeagueGameFinderResults"]
            filtered_games = 0
            for game in games:
                game_date_str = game.get("GAME_DATE", "")
                try:
                    game_date = datetime.strptime(game_date_str, "%Y-%m-%d")
                except ValueError:
                    logging.warning(f"Skipping game with invalid date format: {game_date_str}")
                    continue
                if fetch_all or game_date.date() >= yesterday.date():
                    game_data = {
                        "season_id": game.get("SEASON_ID"),
                        "season": season,
                        "team_id": game.get("TEAM_ID"),
                        "team_abbr": game.get("TEAM_ABBREVIATION"),
                        "team_name": game.get("TEAM_NAME"),
                        "game_id": game.get("GAME_ID"),
                        "game_date": game_date_str,
                        "matchup": game.get("MATCHUP"),
                        "win_loss": game.get("WL"),
                        "points": game.get("PTS"),
                        "fg_pct": game.get("FG_PCT"),
                        "three_pt_pct": game.get("FG3_PCT"),
                        "ft_pct": game.get("FT_PCT"),
                        "reb": game.get("REB"),
                        "ast": game.get("AST"),
                        "tov": game.get("TOV"),
                        "plus_minus": game.get("PLUS_MINUS")
                    }
                    all_games.append(game_data)
                    filtered_games += 1
                    try:
                        message = json.dumps(game_data)
                        publish_message(topic, message)
                        logging.info(f"Published message to topic {topic}: {message}")
                    except Exception as e:
                        logging.error(f"Error publishing message for game {game.get('GAME_ID')}: {e}")
            if filtered_games == 0:
                if fetch_all:
                    logging.info(f"No games found for season {season}.")
                else:
                    logging.info(f"No games found for season {season} from {yesterday.date()} onward.")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Error fetching games for season {season}: {e}")
    return all_games


# NBA upcoming games of the week 
def get_games_week(topic):
    today = datetime.today()
    upcoming_games = [] # 7 days
    for i in range(7):
        day = today + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        try:
            scoreboard = scoreboardv2.ScoreboardV2(game_date=date_str)
            games = scoreboard.get_data_frames()[0]     
            games_list = games.to_dict(orient='records')
            for game in games_list:
                game["GAME_DATE"] = date_str
                upcoming_games.append(game)
                message = json.dumps(game)
                publish_message(topic, message)
                logging.info(f"Published message to topic {topic}: {message}")
        except Exception as e:
            logging.error(f"Error fetching games from date {date_str}: {e}")
    return {"status": "ok", "games_published": len(upcoming_games)}, 200
