import logging
from datetime import datetime
from handlers.get_teams import teams_dict


def remove_fields(message):
    fields_remove = [
        "GAME_DATE_EST", "GAME_SEQUENCE", "GAMECODE", "LIVE_PERIOD", "LIVE_PC_TIME",
        "NATL_TV_BROADCASTER_ABBREVIATION", "HOME_TV_BROADCASTER_ABBREVIATION", 
        "AWAY_TV_BROADCASTER_ABBREVIATION", "LIVE_PERIOD_TIME_BCAST", 
        "ARENA_NAME", "WH_STATUS", "WNBA_COMMISSIONER_FLAG"
    ]
    for field in fields_remove:
        if field in message:
            del message[field]
    return message


# def transform_game_time(game_time_str):
#     try:
#         game_time_str = game_time_str.strip().lower()
#         if 'et' in game_time_str:
#             game_time_str = game_time_str.replace('et', '').strip()
#         game_time = datetime.strptime(game_time_str, "%I:%M %p").time()
#         return game_time
#     except Exception as e:
#         logging.error(f"Error al transformar la hora: {e}")
#         return None
    

def transform_season(season):
    try:
        return f"{season}-{str(int(season) + 1)[2:]}"
    except Exception as e:
        logging.error(f"Error transforming season format: {e}")
        return season


def transform_team_id_to_abbr(payload):
    try:
        # home_team_info = teams_dict.get(payload["HOME_TEAM_ID"], {"abbreviation": "Unknown", "team_name": "Unknown"})
        # payload["team_abbr"] = home_team_info["abbreviation"]
        # payload["team_name"] = home_team_info["team_name"]
        payload["team_id"] = payload.pop("HOME_TEAM_ID") ##### En la tabla de games, el team_id es siempre el equipo que juega en casa

        # visitor_team_info = teams_dict.get(payload["VISITOR_TEAM_ID"], {"abbreviation": "Unknown", "team_name": "Unknown"})
        # payload["visitor_team_abbr"] = visitor_team_info["abbreviation"]
        # payload["away_team"] = visitor_team_info["team_name"]
        # del payload["VISITOR_TEAM_ID"]   
        return payload
    except Exception as e:
        logging.error(f"Error transforming team IDs: {e}")
        return None