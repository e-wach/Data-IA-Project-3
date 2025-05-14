import json
import requests
from nba_api.stats.static import teams

# 1. Obtener equipos desde nba_api
nba_teams = teams.get_teams()
nba_teams_filtered = [{
    "team_id_nba": team["id"],  # antes "team_id"
    "team_name": team["full_name"],
    "abbreviation": team["abbreviation"],
    "nickname": team["nickname"]
} for team in nba_teams]

# 2. Obtener equipos desde SportsData API
API_KEY = ""
url = "https://api.sportsdata.io/v3/nba/scores/json/teams"
headers = {"Ocp-Apim-Subscription-Key": API_KEY}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    sportsdata_teams = response.json()

    # 3. Combinar datos
    combined_teams = []
    for sd_team in sportsdata_teams:
        nba_match = next((t for t in nba_teams_filtered if t["team_id_nba"] == sd_team["NbaDotComTeamID"]), None)
        if nba_match:
            combined = {
                "team_id_nba": nba_match["team_id_nba"],
                "team_id_sd": sd_team["TeamID"],
                "abbreviation": nba_match["abbreviation"],
                "nickname": nba_match["nickname"],
                "team_name": nba_match["team_name"],
                "city": sd_team["City"],
                "name": sd_team["Name"]
            }
            combined_teams.append(combined)

    with open("combined_teams.json", "w") as f:
        json.dump(combined_teams, f, indent=2)

    print("Archivo combinado guardado como combined_teams.json")
else:
    print("Error al obtener equipos de SportsData:", response.status_code)