output "sql_host" {
    description = "SQL Public IP"
    value = google_sql_database_instance.postgres_instance.ip_address
}

output "sql_user" {
    description = "SQL database user"
    value = google_sql_user.postgres_user.name
}

output "sql_pass" {
    description = "SQL database password"
    value = google_sql_user.postgres_user.password
}

output "sql_db" {
    description = "SQL database"
    value = google_sql_database.postgres_db.name
}