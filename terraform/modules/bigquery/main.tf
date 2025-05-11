resource "google_bigquery_dataset" "nba" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_table" "nba_games" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id   = var.table_names.games
  project    = var.project_id
  schema     = file("${path.module}/schemas/schema_games.json")
  deletion_protection = false
  range_partitioning {
    field = "team_id"

    range {
      start    = 1610612737
      end      = 1610612767  # IMPORTANTE: este valor es exclusivo
      interval = 1
    }
  }
}

resource "google_bigquery_table" "nba_games_week" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id   = var.table_names.games_week
  project    = var.project_id
  schema     = file("${path.module}/schemas/schema_games_week.json")
  deletion_protection = false
  range_partitioning {
    field = "team_id"

    range {
      start    = 1610612737
      end      = 1610612767  # IMPORTANTE: este valor es exclusivo
      interval = 1
    }
  }
}

resource "google_bigquery_table" "nba_odds" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id   = var.table_names.odds
  project    = var.project_id
  schema     = file("${path.module}/schemas/schema_theodds_api.json")
  deletion_protection = false
}

resource "google_bigquery_table" "nba_teams" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id   = var.table_names.teams
  project    = var.project_id
  schema     = file("${path.module}/schemas/schema_teams.json")
  deletion_protection = false
}