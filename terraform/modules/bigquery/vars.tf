variable "project_id" {
  type = string
}

variable "dataset_id" {
  type    = string
  default = "nba_dataset"
}

variable "region" {
  type = string
}

variable "table_names" {
  type = object({
    games        = string
    games_week   = string
    odds         = string
    teams        = string
  })

  default = {
    games        = "nba_games"
    games_week   = "nba_games_week"
    odds         = "nba_odds"
    teams        = "nba_teams"
  }
}
