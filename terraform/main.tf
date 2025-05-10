terraform {
  backend "gcs" {
    bucket = var.bucket_state  
    prefix = "terraform/terraform.tfstate"    
  }
}

module "api" {
  source = "./modules/api"
  topic_names = var.topic_names
  region = var.region
  project_id = var.project_id
  api_key_odds = var.api_key_odds
}