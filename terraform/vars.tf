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

variable "table_names" {
  type = object({
    games = string
    teams = string
  })
}

variable "project_number" {
  type = string
}

variable "sql_host" {
  type = string
}

variable "sql_user" {
  type = string
}

variable "sql_pass" {
  type      = string
  sensitive = true
}

variable "sql_db" {
  type    = string
}