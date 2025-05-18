output "sql-api-url" {
    description = "AI Agent endpoint"
    value = google_cloud_run_v2_service.cloudrun-sql-api.uri
}