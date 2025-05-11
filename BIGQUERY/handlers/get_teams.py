import json
import logging


teams_dict = {}

def callback_teams(message):
    try:
        team_info = json.loads(message.data.decode('utf-8'))
        team_id = team_info['team_id']
        team_abbr = team_info['abbreviation']
        team_name = team_info['team_name']
        teams_dict[team_id] = {
            'abbreviation': team_abbr,
            'name': team_name
        }
        # message.ack()
        logging.info("Team information processed successfully.")
    except Exception as e:
        logging.error(f"Error processing team info: {e}")
        message.nack()
