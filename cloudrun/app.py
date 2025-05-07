import os
import json
import logging
from datetime import datetime, timedelta

from flask import Flask
from google.cloud import pubsub_v1
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, scoreboardv2

# Variables de entorno
PROJECT_ID = os.getenv("PROJECT_ID", "western-mix-459018-g4" )
TOPIC_TEAMS = os.getenv("TOPIC_TEAMS", "nba_teams")
TOPIC_GAMES = os.getenv("TOPIC_GAMES", "nba_games")
TOPIC_GAMES_WEEK = os.getenv("TOPIC_GAMES_WEEK", "nba_games_week")

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Función para publicar mensajes
def publish_message(topic, message):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, topic)
    future = publisher.publish(topic_path, message.encode("utf-8"))
    future.result()  # Espera a que se complete

@app.route("/teams", methods=["POST"])
def get_teams():
    try:
        nba_teams = teams.get_teams()
        for team in nba_teams:
            message = json.dumps({
                "team_id": team.get("id"),
                "team_name": team.get("full_name"),
                "nickname": team.get("nickname"),
                "city": team.get("city"),
                "state": team.get("state"),
                "year_founded": team.get("year_founded")
            })
            publish_message(TOPIC_TEAMS, message)
            logging.info(f"Publicado en {TOPIC_TEAMS}: {message}")
        return {"status": "ok", "message": "Equipos publicados"}, 200
    except Exception as e:
        logging.error(f"Error publicando equipos: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route("/games", methods=["POST"])
def get_games():
    seasons = ["2022-23", "2023-24", "2024-25"]
    for season in seasons:
        finder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
        results = finder.get_normalized_dict()["LeagueGameFinderResults"]
        for game in results:
            data = {
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
            try:
                msg = json.dumps(data)
                publish_message(TOPIC_GAMES, msg)
                logging.info(f"Publicado en {TOPIC_GAMES}: {msg}")
            except Exception as e:
                logging.error(f"Error publicando juego {game['GAME_ID']}: {e}")
    return {"status": "ok", "message": "Juegos publicados"}, 200

@app.route("/games_week", methods=["POST"])
def get_games_week():
    try:
        today = datetime.today()
        start_week = today - timedelta(days=today.weekday())
        count = 0
        for i in range(7):
            day = start_week + timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            scoreboard = scoreboardv2.ScoreboardV2(game_date=date_str)
            df = scoreboard.get_data_frames()[0]
            records = df.to_dict(orient="records")
            for record in records:
                record["GAME_DATE"] = date_str
                publish_message(TOPIC_GAMES_WEEK, json.dumps(record))
                logging.info(f"Publicado en {TOPIC_GAMES_WEEK}: {record}")
                count += 1
        return {"status": "ok", "games_published": count}, 200
    except Exception as e:
        logging.error(f"Error publicando juegos semanales: {e}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)