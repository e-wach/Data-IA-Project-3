import requests
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Call to The Odds API
def fetch_odds_data():
    API_KEY = os.environ['API_KEY'] ## cambiarlo por os.getenv() cuando hagamos el TF
    SPORT = 'basketball_nba'
    REGIONS = 'eu' # 'eu,us,uk'
    MARKETS = 'h2h' # 'h2h,spreads,totals'
    ODDS_FORMAT = 'decimal'
    DATE_FORMAT = 'iso' ## 'unix' si queremos con hora
    DAYS_FROM = 7
    try:
        odds_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
            params={
                'api_key': API_KEY,
                'regions': REGIONS,
                'markets': MARKETS,
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': DATE_FORMAT,
                'daysFrom': DAYS_FROM
            }
        )
        if odds_response.status_code != 200:
            logging.error(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
            return {"status": "error", "message": "Failed to get odds"}, 500
        return odds_response.json()
    except Exception as e:
        logging.error(f"Error fetching odds data: {str(e)}")
        return None

def create_market_message(market):
    market_outcomes = []
    for outcome in market.get('outcomes', []):
        outcome_name = outcome.get('name')
        outcome_price = outcome.get('price')
        outcome_point = outcome.get('point', 0)
        market_outcomes.append({
            "name": outcome_name,
            "price": outcome_price,
            "point": outcome_point
        })
    return market_outcomes


def create_bookmaker_message(bookmaker):
    bookmaker_name = bookmaker.get('title', 'Unknown')
    bookmaker_key = bookmaker.get('key', 'Unknown')
    bookmaker_markets = []
    for market in bookmaker.get('markets', []):
        market_key = market.get('key')
        market_outcomes = create_market_message(market)
        if not market_outcomes:
            logging.warning(f"No outcomes found for bookmaker {bookmaker_name}, market {market_key}")
        bookmaker_markets.append({
            "market_key": market_key,
            "outcomes": market_outcomes
        })
    if not bookmaker_markets:
        logging.warning(f"No markets found for bookmaker {bookmaker_name}")
    return {
        "bookmaker_name": bookmaker_name,
        "bookmaker_key": bookmaker_key,
        "markets": bookmaker_markets
    }