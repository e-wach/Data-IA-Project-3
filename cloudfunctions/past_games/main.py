import os
import logging
from google.cloud import bigquery
import functions_framework

PROJECT_ID = os.getenv("GCP_PROJECT", "original-list-459014-b6")
DATASET_ID = os.getenv("BQ_DATASET", "nba_dataset")
NBA_GAMES_TABLE = os.getenv("BQ_TABLE", "nba_games")

bq = bigquery.Client(project=PROJECT_ID)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

@functions_framework.cloud_event
def callback_games(cloud_event):
    bucket_name = cloud_event.data.get("bucket")
    object_name = cloud_event.data.get("name")

    if not object_name or not object_name.endswith(".csv"):
        logging.info(f"Ignoring non-csv file: {object_name}")
        return

    uri = f"gs://{bucket_name}/{object_name}"
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{NBA_GAMES_TABLE}"

    logging.info(f"Starting load from {uri} into {table_ref}")

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=False, 
        schema=[ ######### REVISAR
  { "name": "season",                            "type": "STRING",   "mode": "REQUIRED" },
  { "name": "team_id",                           "type": "INTEGER",  "mode": "NULLABLE" },
  { "name": "team_abbr",                         "type": "STRING",   "mode": "NULLABLE" },
  { "name": "team_name",                         "type": "STRING",   "mode": "NULLABLE" },
  { "name": "possessions",                       "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "game_id",                           "type": "INTEGER",   "mode": "REQUIRED" },
  { "name": "game_date",                         "type": "DATE",     "mode": "NULLABLE" },
  { "name": "year",                              "type": "INTEGER",  "mode": "NULLABLE" },
  { "name": "month",                             "type": "INTEGER",  "mode": "NULLABLE" },
  { "name": "day",                               "type": "INTEGER",  "mode": "NULLABLE" },
  { "name": "date_time",                         "type": "TIME",     "mode": "NULLABLE" },
  { "name": "home_away",                         "type": "STRING",   "mode": "NULLABLE" },
  { "name": "home_team",                         "type": "STRING",   "mode": "NULLABLE" },
  { "name": "away_team",                         "type": "STRING",   "mode": "NULLABLE" },
  { "name": "win_loss",                          "type": "STRING",   "mode": "NULLABLE" },
  { "name": "field_goals_made",                  "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "field_goals_attempted",             "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "field_goals_percentage",            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "effective_field_goals_percentage",  "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "two_pointers_made",                 "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "two_pointers_attempted",            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "two_pointers_percentage",           "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "three_pointers_made",               "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "three_pointers_attempted",          "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "three_pointers_percentage",         "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "free_throws_made",                  "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "free_throws_attempted",             "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "free_throws_percentage",            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "offensive_rebounds",                "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "defensive_rebounds",                "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "rebounds",                          "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "offensive_rebounds_percentage",     "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "defensive_rebounds_percentage",     "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "total_rebounds_percentage",         "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "assists",                           "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "assists_percentage",                "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "steals",                            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "steals_percentage",                 "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "blocked_shots",                     "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "blocks_percentage",                 "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "turnovers",                         "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "turnovers_percentage",              "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "personal_fouls",                    "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "points",                            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "true_shooting_attempts",            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "true_shooting_percentage",          "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "player_efficiency_rating",          "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "usage_rate_percentage",             "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "fantasy_points",                    "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "fantasy_points_fanduel",            "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "fantasy_points_draftkings",         "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "fantasy_points_yahoo",              "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "double_doubles",                    "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "triple_doubles",                    "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "fantasy_points_fantasydraft",       "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "plus_minus",                        "type": "FLOAT",    "mode": "NULLABLE" },
  { "name": "rest_days",                         "type": "INTEGER",  "mode": "NULLABLE" }
],
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        range_partitioning=bigquery.RangePartitioning(
            field="team_id",
            range_=bigquery.PartitionRange(start=1610612737, end=1610612767, interval=1),
        ),
    )
    try:
        load_job = bq.load_table_from_uri(uri, table_ref, job_config=job_config)
        load_job.result()
        logging.info(f"Loaded {load_job.output_rows} rows into {table_ref}")
    except Exception as e:
        logging.error(f"BigQuery load_job failed: {e}")
        raise

