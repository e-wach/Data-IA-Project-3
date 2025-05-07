from google.cloud import pubsub_v1
from flask import Flask
import json
import logging
import requests
import os
from dotenv import load_dotenv

from teams_games import publish_message
from theoddsapi import fetch_odds_data, create_bookmaker_message, create_market_message

from nba_api.live.nba.endpoints import Odds


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


# Odds for today's games
@app.route("/odds", methods=["POST"])
def nba_odds():
    topic = "games_odds"
    odds = Odds()
    games_list = odds.get_games().get_dict()
    try:
        for game in games_list:
            game_id = game.get('gameId')
            home_team_id = game.get('homeTeamId')
            away_team_id = game.get('awayTeamId')

            for market in game.get('markets', []):
                market_name = market.get('name')
                odds_type_id = market.get('odds_type_id')
                group_name = market.get('group_name')
                for book in market.get('books', []):
                    book_id = book.get('id')
                    book_name = book.get('name')
                    book_url = book.get('url')
                    country_code = book.get('countryCode')
                    for outcome in book.get('outcomes', []):
                        odds_type = outcome.get('type')
                        odds_value = outcome.get('odds')
                        opening_odds = outcome.get('opening_odds')
                        odds_trend = outcome.get('odds_trend')
                        message = {
                            "game_id": game_id,
                            "home_team_id": home_team_id,
                            "away_team_id": away_team_id,
                            "market_name": market_name,
                            "odds_type_id": odds_type_id,
                            "group_name": group_name,
                            "book_name": book_name,
                            "country_code": country_code,
                            "book_url": book_url,
                            "odds_type": odds_type,
                            "odds": odds_value,
                            "opening_odds": opening_odds,
                            "odds_trend": odds_trend
                        }
                        message_json = json.dumps(message)
                        publish_message(topic, message_json)
                        logging.info(f"Published odds for game {game_id} - Market: {market_name} - Book: {book_name} - Outcome: {odds_type}")
        return {"status": "ok"}, 200
    except Exception as e:
        logging.error(f"Error publishing message: {e}")
        return {"status": "error", "message": str(e)}, 500


# Endpoint The Odds API
@app.route("/oddsWeek", methods=["POST"])
def nba_odds_week():
    topic_odds = "odds_week" ### Convertir en variable de entorno
    try: 
        odds_json = fetch_odds_data()
        if not odds_json:
            return {"status": "error", "message": "No odds data available"}, 500
        for game in odds_json:
            game_id = game.get('id')
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            message = {
                "game_id": game_id,
                "home_team": home_team,
                "away_team": away_team,
                "bookmakers": []
            }
            for bookmaker in game.get('bookmakers', []):
                bookmaker_message = create_bookmaker_message(bookmaker)
                if bookmaker_message.get("markets"):
                    message["bookmakers"].append(bookmaker_message)
                else:
                    logging.warning(f"Bookmaker {bookmaker_message['bookmaker_name']} has no valid markets.")
            message_json = json.dumps(message)
            publish_message(topic_odds, message_json)
            logging.info(f"Published odds for game {game_id} - {home_team} vs {away_team}")
        return {"status": "ok"}, 200
    except Exception as e:
        logging.error(f"Error in nba_odds_week: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

        
        
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
