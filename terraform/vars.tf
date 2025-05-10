variable "bucket_state" {
    type = string
}

variable "project_id" {
    type = string
}

variable "region" {
    type = string
}

variable topic_names {
    type = list(string)
    default = ["nba_teams", "nba_games", "nba_games_week", "team_metrics", "team_season_stats", "team_stats", "odds_week"]
}

variable "api_key_odds" {
    type = string
}

variable "bucket_state" {
  type = string
}
