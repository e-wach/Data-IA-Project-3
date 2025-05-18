terraform {
  backend "gcs" {
    bucket = "terraform-state-ewach" ######## CAMBIAR!!!
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
  sql_pass = module.cloudsql.sql_pass
  sql_user = module.cloudsql.sql_user
  dataset_id = var.dataset_id
  depends_on = [module.bigquery]
}

module "bigquery" {
source          = "./modules/bigquery"
  project_id      = var.project_id
  region          = var.region
  dataset_id      = var.dataset_id
  bucket_name     = var.bucket_name
  bq_table = var.bq_table
}

module "cloudsql" {
  source = "./modules/cloudsql"
  region = var.region
}

module "api-agent" {
  source = "./modules/api-agent"
  region = var.region
  project_id = var.project_id
  sql_host = module.cloudsql.sql_host
  sql_db = module.cloudsql.sql_db
  sql_pass = module.cloudsql.sql_pass
  sql_user = module.cloudsql.sql_user
}

module "cloudfunctions" {
  source = "./modules/cloudfunctions"
  region = var.region
  project_id = var.project_id
  dataset_id = var.dataset_id
  bq_table = var.bq_table
  bucket_name = var.bucket_name
  topic_names = var.topic_names
  sql_host = module.cloudsql.sql_host
  sql_db = module.cloudsql.sql_db
  sql_pass = module.cloudsql.sql_pass
  sql_user = module.cloudsql.sql_user
  depends_on = [module.bigquery, module.api, module.cloudsql]
}