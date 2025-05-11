import json
import logging
from nba_api.live.nba.endpoints import Odds

from publisher import publish_message

logging.basicConfig(level=logging.DEBUG)


def nba_odds(topic):
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
