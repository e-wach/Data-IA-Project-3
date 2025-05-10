variable "topic_names" {
  type = object({
    teams      = string
    games      = string
    games_week = string
    stats      = string
    odds       = string
  })
}

variable "region" {
    type = string
}

variable "project_id" {
    type = string
}

variable "api_key_odds" {
    type = string
}

variable "service_name" {
  type = string
}

variable "image_url" {
  type = string
}
