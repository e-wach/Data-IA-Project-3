from nba_api.stats.endpoints import leaguegamefinder
import json

gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00", season_nullable='2023-24')
games_df = gamefinder.get_data_frames()[0]

# Convertir el DataFrame a JSON (como lista de diccionarios)
games_json = games_df.to_dict(orient='records')

with open('games2324.json', 'w') as f:
    f.write(json.dumps(games_json,indent=4))

with open('games2324.csv', 'w') as f:
    games_df.to_csv(f, index=False)