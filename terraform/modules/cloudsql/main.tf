resource "google_sql_database_instance" "postgres_instance" {
  name             = "nba_postgres"
  region           = var.region
  database_version = "POSTGRES_15"
  deletion_protection = false
  settings {
    tier            = "db-f1-micro" 
    availability_type = "ZONAL"
    disk_size       = 100 

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "public-access"
        value = "0.0.0.0/0"
      }
    }
  }
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_sql_user" "postgres_user" {
  name     = "nba_user"
  instance = google_sql_database_instance.postgres_instance.name
  password = "dataproject3"
}

resource "google_sql_database" "postgres_db" {
  name     = "nba_database"
  instance = google_sql_database_instance.postgres_instance.name
}