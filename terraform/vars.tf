variable "project_id" {
    type = string
}

variable "region" {
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
    games        = string
    # games_week   = string
    # odds         = string
    teams        = string
  })

  default = {
    games        = "nba_games"
    # games_week   = "nba_games_week"
    # odds         = "nba_odds"
    teams        = "nba_teams"
  }
}
