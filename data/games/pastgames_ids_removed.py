from nba_api.stats.endpoints import leaguegamefinder
from datetime import datetime
import pandas as pd
import logging

logging.basicConfig(level=logging.WARNING)

SEASONS = ['2022-23', '2023-24', '2024-25']
CUTOFF_DATE = "2025-05-11"

# IDs a eliminar
REMOVE_IDS = [
    12315, 12325, 15019, 15020, 15022, 15025, 50009,
    1610616833, 1610616834, 1610616839, 1610616840,
    1610616847, 1610616848
]

def transform_game_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        logging.warning(f"Invalid game date format: {s}")
        return None

def transform_matchup(m):
    if " vs." in m:
        h, a = m.split(" vs.")
        return h.strip(), a.strip(), "home"
    elif " @" in m:
        a, h = m.split(" @")
        return h.strip(), a.strip(), "away"
    else:
        return m, m, None

def calculate_rest_days(df, date_col='game_date'):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col], format="%Y-%m-%d", errors="coerce")
    d = d.sort_values(['team_id', date_col]).reset_index(drop=True)
    d['rest_days'] = d.groupby('team_id')[date_col].diff().dt.days.fillna(0).astype(int)
    return d

# 1) Retrieve and transform data for each season
frames = []
for season in SEASONS:
    finder = leaguegamefinder.LeagueGameFinder(league_id_nullable="00", season_nullable=season)
    df_season = finder.get_data_frames()[0]
    df_season['game_date'] = df_season['GAME_DATE'].apply(transform_game_date)
    df_season[['home_team','away_team','home_away']] = df_season['MATCHUP'].apply(
        lambda x: pd.Series(transform_matchup(x))
    )
    df_season['season'] = season
    frames.append(df_season)

# 2) Concatenate and filter by cutoff date
df = pd.concat(frames, ignore_index=True)
df = df[df['game_date'] <= CUTOFF_DATE]

# 3) Extract year/month/day
df['game_date'] = pd.to_datetime(df['game_date'], format="%Y-%m-%d", errors="coerce")
df['year']  = df['game_date'].dt.year
df['month'] = df['game_date'].dt.month
df['day']   = df['game_date'].dt.day

# 4) Lowercase and dedupe column names
df.columns = df.columns.str.lower()
df = df.loc[:, ~df.columns.duplicated()]

# 5) Calculate rest_days
df = calculate_rest_days(df, date_col='game_date')

# 6) Rename to match schema_games.json
df = df.rename(columns={
    'team_abbreviation': 'team_abbr',
    'wl':               'win_loss',
    'pts':              'points',
    'fgm':              'field_goals_made',
    'fga':              'field_goals_attempted',
    'fg_pct':           'field_goals_percentage',
    'efg_pct':          'effective_field_goals_percentage',
    'fg2m':             'two_pointers_made',
    'fg2a':             'two_pointers_attempted',
    'fg2_pct':          'two_pointers_percentage',
    'fg3m':             'three_pointers_made',
    'fg3a':             'three_pointers_attempted',
    'fg3_pct':          'three_pointers_percentage',
    'ftm':              'free_throws_made',
    'fta':              'free_throws_attempted',
    'ft_pct':           'free_throws_percentage',
    'oreb':             'offensive_rebounds',
    'dreb':             'defensive_rebounds',
    'reb':              'rebounds',
    'oreb_pct':         'offensive_rebounds_percentage',
    'dreb_pct':         'defensive_rebounds_percentage',
    'reb_pct':          'total_rebounds_percentage',
    'ast':              'assists',
    'ast_pct':          'assists_percentage',
    'stl':              'steals',
    'stl_pct':          'steals_percentage',
    'blk':              'blocked_shots',
    'blk_pct':          'blocks_percentage',
    'tov':              'turnovers',
    'tov_pct':          'turnovers_percentage',
    'pf':               'personal_fouls',
    'pts_fantasy':      'fantasy_points',
    'pts_fanduel':      'fantasy_points_fanduel',
    'pts_draftkings':   'fantasy_points_draftkings',
    'pts_yahoo':        'fantasy_points_yahoo',
    'dbl_dbl':          'double_doubles',
    'tpl_dbl':          'triple_doubles',
    'pts_fdraft':       'fantasy_points_fantasydraft',
    'plus_minus':       'plus_minus'
})

# 7) Ensure every schema field exists (fill missing with NA)
schema_fields = [
    'season','team_id','team_abbr','team_name','possessions','game_id',
    'game_date','year','month','day','date_time','home_away','home_team',
    'away_team','win_loss','field_goals_made','field_goals_attempted',
    'field_goals_percentage','effective_field_goals_percentage',
    'two_pointers_made','two_pointers_attempted','two_pointers_percentage',
    'three_pointers_made','three_pointers_attempted','three_pointers_percentage',
    'free_throws_made','free_throws_attempted','free_throws_percentage',
    'offensive_rebounds','defensive_rebounds','rebounds',
    'offensive_rebounds_percentage','defensive_rebounds_percentage',
    'total_rebounds_percentage','assists','assists_percentage','steals',
    'steals_percentage','blocked_shots','blocks_percentage','turnovers',
    'turnovers_percentage','personal_fouls','points',
    'true_shooting_attempts','true_shooting_percentage',
    'player_efficiency_rating','usage_rate_percentage','fantasy_points',
    'fantasy_points_fanduel','fantasy_points_draftkings',
    'fantasy_points_yahoo','double_doubles','triple_doubles',
    'fantasy_points_fantasydraft','plus_minus','rest_days'
]
for col in schema_fields:
    if col not in df.columns:
        df[col] = pd.NA

# 8) Drop everything else and reorder
df = df[schema_fields]

# — NUEVO PASO: filtrar los team_id no deseados —
df = df[~df['team_id'].isin(REMOVE_IDS)]

# 9) Export final CSV
df.to_csv("years_22-25_no_ids.csv", index=False)
