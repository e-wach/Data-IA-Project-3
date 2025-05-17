resource "google_artifact_registry_repository" "sql_api_repo" {
  location      = var.region
  repository_id = "sql-api"
  format        = "DOCKER"
}

locals {
    image_path = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.sql_api_repo.repository_id}/sql_api:latest"
  }


resource "null_resource" "docker_build_push_api_agent" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${local.image_path} -f ../API-AI/Dockerfile ../API-AI && docker push ${local.image_path}
    EOT
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [google_artifact_registry_repository.sql_api_repo]
}

## Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun-sql-api" {
    name = "sql-api"
    location = var.region
    deletion_protection = false
    ingress = "INGRESS_TRAFFIC_ALL"
    template {
        containers {
            image = local.image_path
            env {
                name = "PROJECT_ID"
                value = var.project_id
            }
            env {
                name = "SQL_HOST"
                value = var.sql_host
            }
            env {
                name = "SQL_USER"
                value = var.sql_user
            }
            env {
                name = "SQL_PASS"
                value = var.sql_pass
            }
            env {
                name = "SQL_DB"
                value = var.sql_db
            }
            ports {
                container_port = 8000
            }
        }
        }
    depends_on = [google_artifact_registry_repository.sql_api_repo, null_resource.docker_build_push_api_agent]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project = google_cloud_run_v2_service.cloudrun-sql-api.project
  location = google_cloud_run_v2_service.cloudrun-sql-api.location
  name = google_cloud_run_v2_service.cloudrun-sql-api.name
  role = "roles/run.invoker"
  member = "allUsers"

  depends_on = [google_cloud_run_v2_service.cloudrun-sql-api]
}