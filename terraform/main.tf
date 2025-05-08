terraform {
  backend "gcs" {
    bucket = "terraform-state-ewach"  
    prefix = "terraform/terraform.tfstate"    
  }
}

module "api" {
  source = "./modules/api"
  topic_names = var.topic_names
}