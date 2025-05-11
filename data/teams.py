import json
from nba_api.stats.static import teams

nba_teams = teams.get_teams()

nba_teams_filtered = [{
        "team_id": team["id"],
        "team_name": team["full_name"],
        "abbreviation": team["abbreviation"],
        "nickname": team["nickname"]
    }
    for team in nba_teams
]


with open('nba_teams.json', 'w') as f:
    json.dump(nba_teams_filtered, f, indent=4)

print("Archivo 'nba_teams.json' guardado correctamente.")

