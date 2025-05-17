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

variable "bq_table" {
  type = string
}

variable "sql_host" {
    type = string
}

variable "sql_user" {
    type = string
}

variable "sql_pass" {
    type = string
}

variable "sql_db" {
    type = string
}