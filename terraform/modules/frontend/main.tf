resource "google_artifact_registry_repository" "agent-repo" {
  location      = var.region
  repository_id = "agent-repo"
  format        = "DOCKER"
}

locals {
    image_path = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.agent-repo.repository_id}/agent:latest"
  }

########## TODAVÍA NO ESTÁ LA IMAGEN
resource "null_resource" "docker_build_push_api" {
  provisioner "local-exec" {
    command = <<EOT
      docker build -t ${local.image_path} -f ../docker/Dockerfile ../docker && docker push ${local.image_path} 
    EOT
  }
  triggers = {
    always_run = timestamp()
  }
  depends_on = [google_artifact_registry_repository.agent-repo]
}

## Cloud Run Service
resource "google_cloud_run_v2_service" "cloudrun-agent" {
    name = "agent-cloudrun"
    location = var.region
    deletion_protection = false
    ingress = "INGRESS_TRAFFIC_ALL"
    template {
        containers {
            image = local.image_path
            ports {
                container_port = 8080
            }
        }
        }
    depends_on = [google_artifact_registry_repository.agent-repo, null_resource.docker_build_push_api]
}
