resource "google_pubsub_topic" "pubsub_topics" {
    count = length(var.topic_names)
    name = var.topic_names[count.index]
}

resource "google_pubsub_subscription" "pubsub_subs" {
    count = length(var.topic_names)
    topic = google_pubsub_topic.pubsub_topics[count.index].name
    name = "${var.topic_names[count.index]}-sub"
}


# CLOUD RUN - API
# Artifact Registry repo
resource "google_artifact_registry_repository" "api_repo" {
  location      = var.region
  repository_id = "nba-api-repo"
  format        = "DOCKER"
}

locals {
    image_path = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.api_repo.repository_id}/nba_api:latest"
  }


resource "null_resource" "docker_build_push_api" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${local.image_path} -f ../API/Dockerfile ../API && docker push ${local.image_path}
    EOT
  }
  # triggers = {
  #   always_run = timestamp()
  # }
  depends_on = [google_artifact_registry_repository.api_repo, google_pubsub_topic.pubsub_topics]
}


## Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun-api" {
    name = "nbaapi"
    location = var.region
    deletion_protection = false
    ingress = "INGRESS_TRAFFIC_ALL"
     
    template {
        service_account = google_service_account.cloudbuild_service_account.account_id
        containers {
            image = local.image_path
            env {
                name = "PROJECT_ID"
                value = var.project_id
            }
            env {
                name = "API_KEY_ODDS"
                value = var.api_key_odds
            }
            env {
                name = "API_KEY_SD"
                value = var.api_key_sd
            }
            # env {
            #     name = "SQL_HOST"
            #     value = var.sql_host
            # }
            # env {
            #     name = "SQL_USER"
            #     value = var.sql_user
            # }
            # env {
            #     name = "SQL_PASS"
            #     value = var.sql_pass
            # }
            # env {
            #     name = "SQL_DB"
            #     value = var.sql_db
            # }
            dynamic "env" {
                for_each = var.topic_names
                content {
                    name = "TOPIC_${env.value}"
                    value = env.value
                }
            }
            ports {
                container_port = 8080
            }
        }
    }
    depends_on = [google_pubsub_topic.pubsub_topics,google_artifact_registry_repository.api_repo, 
    null_resource.docker_build_push_api, 
    google_service_account.cloudbuild_service_account,
    google_project_iam_member.act_as, 
    google_project_iam_member.bigquery_reader, 
    google_project_iam_member.cloudsql_client, 
    google_project_iam_member.pubsub_publisher]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project = google_cloud_run_v2_service.cloudrun-api.project
  location = google_cloud_run_v2_service.cloudrun-api.location
  name = google_cloud_run_v2_service.cloudrun-api.name
  role = "roles/run.invoker"
  member = "allUsers"

  depends_on = [google_cloud_run_v2_service.cloudrun-api]
}

# Service account for Cloud Run
resource "google_service_account" "cloudbuild_service_account" {
  account_id = "build-sa"
}

resource "google_project_iam_member" "act_as" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_project_iam_member" "pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_project_iam_member" "bigquery_reader" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}
resource "google_project_iam_member" "logs_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cloudbuild_service_account.email}"
}


# Google Scheduler API (daily invoker)
resource "google_cloud_scheduler_job" "api-job" {
  name             = "dailyapi"
  description      = "Daily invoke API"
  schedule         = "0 13 * * * "
  time_zone        = "Europe/Madrid"
  attempt_deadline = "180s"

  retry_config {
    retry_count = 2
  }

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.cloudrun-api.uri}/daily/all"
    }
  }
