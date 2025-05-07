import requests
import os
import json
import logging
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
load_dotenv()

API_KEY = os.environ['API_KEY'] ## cambiarlo por os.getenv() cuando hagamos el TF
SPORT = 'basketball_nba'
REGIONS = 'eu,us,uk'
MARKETS = 'h2h,spreads,totals'
'''
h2h: Las apuestas Head-to-Head (quién ganará).

spreads: Apuestas sobre el margen de victoria.

totals: Apuestas sobre el total combinado de puntos de ambos equipos.
'''
ODDS_FORMAT = 'decimal'
DATE_FORMAT = 'iso' ## 'unix' si queremos con hora
DAYS_FROM = 7

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
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    # with open('odds_results.json', 'w') as json_file:
    #     json.dump(odds_json, json_file, indent=4)

    print('Remaining requests:', odds_response.headers['x-requests-remaining'])
    print('Used requests:', odds_response.headers['x-requests-used'])