terraform {
  backend "gcs" {
    bucket = "terraformstatedp3"
    prefix = "terraform/terraform.tfstate"
  }
}

module "api" {
  source = "./modules/api"
  topic_names = var.topic_names
  region = var.region
  project_id = var.project_id
  api_key_odds = var.api_key_odds
  api_key_sd = var.api_key_sd
  sql_host = module.cloudsql.sql_host
  sql_db = module.cloudsql.sql_db
  sql_pass = module.cloudsql.pass
  sql_user = module.cloudsql.user
}

module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  dataset_id = var.dataset_id
  region = var.region
}

module "cloudsql" {
  source = "./modules/cloudsql"
  region = var.region
}