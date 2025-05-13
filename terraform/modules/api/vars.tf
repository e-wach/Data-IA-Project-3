variable topic_names {
    type = list(string)
}

variable "region" {
    type = string
}

variable "project_id" {
    type = string
}

variable "api_key_odds" {
    type = string
    sensitive = true
}

variable "api_key_sd" {
    type = string
    sensitive = true
}