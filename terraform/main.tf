terraform {
  backend "gcs" {}
}

module "api" {
  source = "./modules/api"
  topic_names = var.topic_names
  region = var.region
  project_id = var.project_id
  api_key_odds = var.api_key_odds
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  dataset_id = "nba_dataset"
  region = var.region

  table_names = {
    games        = "nba_games"
    games_week   = "nba_games_week"
    odds         = "nba_odds"
    teams        = "nba_teams"
  }
}