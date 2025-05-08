# Pub/Sub topics and subscriptions
resource "google_pubsub_topic" "pubsub_topics" {
    count = length(var.topic_names)
    name = var.topic_names[count.index]
}

resource "google_pubsub_subscription" "pubsub_subs" {
    count = length(var.topic_names)
    topic = google_pubsub_topic.pubsub_topics[count.index].name
    name = "${var.topic_names[count.index]}-sub"
}


# CloudRun - API
## Artifact Registry repo
resource "google_artifact_registry_repository" "my-repo" {
  location      = var.region
  repository_id = "nba-api-repo"
  format        = "DOCKER"
}

