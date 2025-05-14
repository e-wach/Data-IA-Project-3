terraform {
  backend "gcs" {}
}

module "api" {
  source = "./modules/api"
  topic_names = var.topic_names
  region = var.region
  project_id = var.project_id
  api_key_odds = var.api_key_odds
  api_key_sd = var.api_key_sd
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  dataset_id = var.dataset_id
  region = var.region
  table_names = var.table_names
}

module "cloudsql" {
  source = "./modules/cloudsql"
  region = var.region
}