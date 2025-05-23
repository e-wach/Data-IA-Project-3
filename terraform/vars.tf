variable "project_id" {
    type = string
}

variable "region" {
    type = string
}

variable "bucket_name" {
  type = string
}

variable "topic_names" {
    type = list(string)
}

variable "api_key_odds" {
    type = string
    sensitive = true
}

variable "api_key_sd" {
    type = string
    sensitive = true
}

variable "dataset_id" {
  type    = string
}

variable "bq_table" {
  type = string
}

variable "gemini_key" {
    type = string
    sensitive = true
}