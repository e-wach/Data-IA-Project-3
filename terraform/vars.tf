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