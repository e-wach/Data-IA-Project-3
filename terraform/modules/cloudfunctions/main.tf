# Cloud Function para leer de pub/sub y cargar en BigQuery

resource "google_storage_bucket_object" "function_zip" {
  name   = "games.zip"
  bucket = var.bucket_name
  source = "${path.module}/zip/games.zip"
}

resource "google_cloudfunctions2_function" "callback_games" {
  name        = "recentgames"
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
    ingress_settings   = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
    environment_variables = {
      PROJECT_ID = var.project_id
      BQ_DATASET     = var.dataset_id
      NBA_GAMES_TABLE    = var.bq_table
    }
  }
  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = format("projects/%s/topics/%s", var.project_id, var.topic_names[0])
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

resource "google_cloudfunctions2_function_iam_member" "unauthenticated_invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.callback_games.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
  depends_on = [google_cloudfunctions2_function.callback_games]
}