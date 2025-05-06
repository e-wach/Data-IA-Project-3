from google.cloud import pubsub_v1
import os
from flask import Flask
import json
import logging
from datetime import datetime, timedelta

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-gcp-project-id")
########### TOPICS (os)
PROJECT_ID = "original-list-459014-b6"

def publish_message(topic, message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, message.encode("utf-8"))


# NBA teams
@app.route("/teams", methods=["POST"])
def get_teams():
    nba_teams = teams.get_teams()
    topic = "nba_teams" # pasar como variable de entorno
    try:
        for team in nba_teams:
            message = json.dumps({
                "team_id": team.get("id"), 
                "team_name": team.get("full_name"), 
                "nickname": team.get("nickname"),
                "city": team.get("city"),
                "state": team.get("state"),
                "year_founded": team.get("year_founded")
            })
            publish_message(topic, message)
            logging.info(f"Published message to topic {topic}: {message}")
        return {"status": "ok", "message": "Teams published"}, 200
    except Exception as e:
        logging.error(f"Error publishing message: {e}")
        return {"status": "error", "message": str(e)}, 500


# NBA completed games
@app.route("/games", methods=["POST"])
def get_games():
    topic = "nba_games"  # pasar como variable de entorno
    seasons = ["2022-23", "2023-24", "2024-25"]
    all_games = []
    for season in seasons:
        gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        games = gamefinder.get_normalized_dict()["LeagueGameFinderResults"]
        for game in games:
            game_data = {
                "season_id": game["SEASON_ID"],
                "season": season,
                "team_id": game["TEAM_ID"],
                "team_abbr": game["TEAM_ABBREVIATION"],
                "team_name": game["TEAM_NAME"],
                "game_id": game["GAME_ID"],
                "game_date": game["GAME_DATE"],
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


# NBA upcoming games of the week 
########### TEAMS EN CÓDIGO / HORA EN STRING (ET)
@app.route("/games_week", methods=["POST"])
def get_games_week():
    topic = "nba_games_week" # pasar como variable de entorno
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)