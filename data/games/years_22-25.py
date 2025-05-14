from nba_api.stats.endpoints import leaguegamefinder
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING)

SEASONS = ['2022-23', '2023-24', '2024-25']
CUTOFF_DATE = "2025-05-11"

# Función para normalizar formato de fecha
def transform_game_date(game_date_str):
    try:
        return datetime.strptime(game_date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        logging.warning(f"Invalid game date format: {game_date_str}")
        return None

# Función para desglosar "MATCHUP" en equipos y tipo de campo
def transform_matchup(matchup):
    if " vs." in matchup:
        home_team, away_team = matchup.split(" vs.")
        return home_team.strip(), away_team.strip(), "home"
    elif "@" in matchup:
        away_team, home_team = matchup.split(" @")
        return home_team.strip(), away_team.strip(), "away"
    else:
        return matchup, matchup, None

# Función para calcular días de descanso (rest days) entre partidos
def calculate_rest_days(df, date_column='GAME_DATE'):
    data = df.copy()
    # Asegurar que la columna de fecha sea tipo datetime (formato YYYY-MM-DD)
    data[date_column] = pd.to_datetime(data[date_column], format="%Y-%m-%d", errors="coerce")
    # Ordenar por equipo y fecha
    data = data.sort_values(["TEAM_ID", date_column]).reset_index(drop=True)
    # Calcular diferencia en días
    data['REST_DAYS'] = (
        data.groupby('TEAM_ID')[date_column]
            .diff()
            .dt.total_seconds() / (24 * 60 * 60)
    )
    # Llenar NaN para el primer partido de cada equipo con 0
    data['REST_DAYS'] = data['REST_DAYS'].fillna(0).astype(int)
    return data

all_seasons_df = []

for season in SEASONS:
    gamefinder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00", season_nullable=season)
    games_df = gamefinder.get_data_frames()[0]

    # Transformaciones base
    games_df["GAME_DATE"] = games_df["GAME_DATE"].apply(transform_game_date)
    games_df[["HOME_TEAM", "AWAY_TEAM", "HOME_AWAY"]] = games_df["MATCHUP"].apply(
        lambda x: pd.Series(transform_matchup(x))
    )
    games_df["SEASON"] = season
    all_seasons_df.append(games_df)

# Concatenar y filtrar por la fecha límite
final_df = pd.concat(all_seasons_df, ignore_index=True)
final_df = final_df[final_df["GAME_DATE"] <= CUTOFF_DATE]

# Convertir GAME_DATE a datetime para extraer year/month/day
final_df["GAME_DATE"] = pd.to_datetime(final_df["GAME_DATE"], format="%Y-%m-%d", errors="coerce")
# Añadir columnas separadas
final_df["year"]  = final_df["GAME_DATE"].dt.year
final_df["month"] = final_df["GAME_DATE"].dt.month
final_df["day"]   = final_df["GAME_DATE"].dt.day

# Calcular y añadir días de descanso
final_df = calculate_rest_days(final_df)

# Poner todos los nombres de columnas en minúsculas
final_df.columns = final_df.columns.str.lower()

# Exportar a CSV conservando la columna original GAME_DATE y las nuevas columnas
final_df.to_csv("years_22-25.csv", index=False)
