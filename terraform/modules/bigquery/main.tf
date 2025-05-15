resource "google_bigquery_dataset" "nba" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.region
}

resource "google_bigquery_table" "nba_games" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id   = "nba_games"
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

