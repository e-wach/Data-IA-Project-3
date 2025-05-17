# Cloud Function from PubSub to BigQuery (nba_games) for most recent games (API SPORTS DATA)
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


# Cloud Functions from PubSub to CloudSQL (nba_games_week)
resource "google_storage_bucket_object" "function_zip_upcoming" {
  name   = "games.zip"
  bucket = var.bucket_name
  source = "${path.module}/zip/upcoming_games.zip"
}
resource "google_cloudfunctions2_function" "upcoming_games" {
  name        = "upcominggamestosql"
  location    = var.region
  project     = var.project_id

  build_config {
    runtime     = "python312"
    entry_point = "callback_upcoming_games"
    source {
      storage_source {
        bucket = var.bucket_name
        object = google_storage_bucket_object.function_zip_upcoming.name
      }
    }
  }
  service_config {
    available_memory   = "256M"
    timeout_seconds    = 60
    environment_variables = {
      PROJECT_ID = var.project_id
      SQL_HOST   = var.sql_host
      SQL_USER   = var.sql_user
      SQL_PASS   = var.sql_pass
      SQL_DB     = var.sql_db
    }
  }
  event_trigger {
    event_type    = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic  = "projects/${var.project_id}/topics/${var.topic_names[1]}"
    trigger_region = var.region
  }
}

resource "google_cloudfunctions2_function_iam_member" "unauthenticated_invoker_upcoming" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.upcoming_games.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
  depends_on = [google_cloudfunctions2_function.upcoming_games]
}
