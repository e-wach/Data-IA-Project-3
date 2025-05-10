data "google_project" "project" {}

# PUB/SUB topics and subscriptions
resource "google_pubsub_topic" "pubsub_topics" {
  for_each = var.topic_names
  name     = each.value
}

resource "google_pubsub_subscription" "pubsub_subs" {
  for_each = var.topic_names
  topic    = google_pubsub_topic.pubsub_topics[each.key].name
  name     = "${each.value}-sub"
}

# CLOUD RUN - API
## Artifact Registry repo
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
  triggers = {
    always_run = timestamp()
  }
  depends_on = [google_artifact_registry_repository.api_repo]
}

## Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun-api" {
    name = var.service_name
    location = var.region
    deletion_protection = false
    ingress = "INGRESS_TRAFFIC_ALL" ### "INGRESS_INTERNAL_ONLY"
    template {
        containers {
            image = local.image_path
            env {
                name = "PROJECT_ID"
                value = var.project_id
            }
            env {
                name = "API_KEY"
                value = var.api_key_odds
            }
            dynamic "env" {
                for_each = var.topic_names
                content {
                    name = "TOPIC_${env.key}"
                    value = env.value
                }
            }
            ports {
                container_port = 8080
            }
        }
    }
    depends_on = [google_artifact_registry_repository.api_repo, null_resource.docker_build_push_api]
}

## PERMISOS 
resource "google_cloud_run_v2_service_iam_member" "private_invoker" {
  project = google_cloud_run_v2_service.cloudrun-api.project
  location = google_cloud_run_v2_service.cloudrun-api.location
  name = google_cloud_run_v2_service.cloudrun-api.name
  role = "roles/run.invoker"
  member = "serviceAccount:service-${data.google_project.project.number}@serverless-robot-prod.iam.gserviceaccount.com"

  depends_on = [google_cloud_run_v2_service.cloudrun-api]
}
