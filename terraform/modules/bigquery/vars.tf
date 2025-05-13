variable "project_id" {
  type = string
}

variable "dataset_id" {
  type    = string
}

variable "region" {
  type = string
}

variable "table_names" {
  type = object({
    games        = string
    # games_week   = string
    # odds         = string
    teams        = string
  })
}
