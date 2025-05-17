resource "google_storage_bucket" "function_bucket" {
  name     = var.bucket_name
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_bigquery_dataset" "nba" {
  dataset_id = var.dataset_id
  project = var.project_id
  location = var.region
}

resource "google_bigquery_table" "nba_games" {
  dataset_id = google_bigquery_dataset.nba.dataset_id
  table_id = "nba_games"
  project = var.project_id
  schema = file("${path.module}/schemas/schema_games.json")
  deletion_protection = false
  range_partitioning {
    field = "team_id"

    range {
      start    = 1610612737
      end      = 1610612767  
      interval = 1
    }
  }
}

# Cloud Function para leer de pub/sub y cargar en BigQuery

resource "google_storage_bucket_object" "function_zip" {
  name   = "games.zip"
  bucket = var.bucket_name
  source = "${path.module}/zip/games.zip"

  depends_on = [google_storage_bucket.function_bucket]
}

resource "google_cloudfunctions2_function" "callback_games" {
  name        = "callbackgames"
  location    = var.region
  project     = var.project_id
  description = "Consume mensajes de Pub/Sub y los inserta en BigQuery"

  build_config {
    runtime     = "python312"
    entry_point = "callback_games"
    source {
      storage_source {
        bucket = var.bucket_name
        object = google_storage_bucket_object.function_zip.name
      }
    }
  }

  service_config {
    min_instance_count = 0
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
    ingress_settings   = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true

    environment_variables = {
      GCP_PROJECT_ID = var.project_id
      BQ_DATASET     = var.dataset_id
      GAMES_TABLE    = google_bigquery_table.nba_games.table_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = format("projects/%s/topics/%s", var.project_id, var.topic_names[0])
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [google_bigquery_table.nba_games]
}

# Cloud Function para cargar CSV histórico de juegos pasados en BigQuery 

resource "google_storage_bucket_object" "past_games_function_zip" {
  name   = "past_games.zip"
  bucket = var.bucket_name
  source = "${path.module}/zip/past_games.zip"

  depends_on = [google_storage_bucket.function_bucket]
}

resource "google_cloudfunctions2_function" "callback_past_games" {
  name        = "callbackpastgames"
  location    = var.region
  project     = var.project_id
  description = "Carga los partidos históricos desde CSV en BigQuery cuando se sube al bucket"

  build_config {
    runtime     = "python312"
    entry_point = "callback_games"
    source {
      storage_source {
        bucket = var.bucket_name
        object = google_storage_bucket_object.past_games_function_zip.name
      }
    }
  }

  service_config {
    min_instance_count = 0
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 60
    ingress_settings   = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true

    environment_variables = {
      GCP_PROJECT_ID = var.project_id
      BQ_DATASET     = var.dataset_id
      BQ_TABLE       = google_bigquery_table.nba_games.table_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    event_filters {
      attribute = "bucket"
      value     = var.bucket_name
    }
    retry_policy = "RETRY_POLICY_RETRY"
  }

  depends_on = [google_bigquery_table.nba_games]
}

resource "google_storage_bucket_object" "past_games_csv" {
  name   = "past_games.csv"
  bucket = var.bucket_name
  source = "${path.module}/../../../data/games/games22-25.csv"

  depends_on = [
    google_bigquery_table.nba_games,
    google_cloudfunctions2_function.callback_past_games
  ]
}