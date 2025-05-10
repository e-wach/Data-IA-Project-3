variable "project_id" {
    type = string
}

variable "region" {
    type = string
}

variable "topic_names" {
  type = object({
    teams      = string
    games      = string
    games_week = string
    stats      = string
    odds       = string
  })
}

variable "api_key_odds" {
    type = string
}

variable "api_image" {
    type = string
}

variable "service_name" {
  type = string
}