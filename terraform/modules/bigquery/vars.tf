variable "project_id" {
  type = string
}

variable "dataset_id" {
  type    = string
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

variable "table_names" {
  type = object({
    games = string
    teams = string
  })
}

variable "project_number" {
  type = string 
}