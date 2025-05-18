resource "google_artifact_registry_repository" "agent-repo" {
  location      = var.region
  repository_id = "ai-agent-repo"
  format        = "DOCKER"
}

locals {
    image_path = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agent-repo.repository_id}/agent:latest"
  }

resource "null_resource" "docker_build_push_agent" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${local.image_path} -f ../AI-agent/Dockerfile ../AI-agent && docker push ${local.image_path} 
    EOT
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [google_artifact_registry_repository.agent-repo]
}

## Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun-agent" {
    name = "ai-agent-endpoint"
    location = var.region
    deletion_protection = false
    ingress = "INGRESS_TRAFFIC_ALL"
    template {
        containers {
            image = local.image_path
            ports {
                container_port = 8008
            }
            env {
                name = "SQL_API"
                value = var.sql-api-url
            }
            env {
                name = "GEMINI_API_KEY"
                value = var.gemini_key
            }
        }
        }
    depends_on = [google_artifact_registry_repository.agent-repo, null_resource.docker_build_push_agent]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project = google_cloud_run_v2_service.cloudrun-agent.project
  location = google_cloud_run_v2_service.cloudrun-agent.location
  name = google_cloud_run_v2_service.cloudrun-agent.name
  role = "roles/run.invoker"
  member = "allUsers"

  depends_on = [google_cloud_run_v2_service.cloudrun-agent]
}