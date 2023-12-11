resource "google_sql_database_instance" "dolfin_database_instance" {
  name                = var.project_name
  database_version    = "MYSQL_5_7"
  region              = var.region
  deletion_protection = false
  settings {
    tier = "db-f1-micro"
    availability_type = "ZONAL"
    ip_configuration {
      ipv4_enabled    = true
      private_network = var.vpc_network_self_link
    }
  }
}

resource "google_sql_database" "users_database" {
  name      = "users"
  instance  = google_sql_database_instance.dolfin_database_instance.name
  charset   = "utf8"
  collation = "utf8_general_ci"
}

resource "google_sql_database" "transactions_database" {
  name      = "transactions"
  instance  = google_sql_database_instance.dolfin_database_instance.name
  charset   = "utf8"
  collation = "utf8_general_ci"
}

resource "google_sql_user" "users" {
  name      = "root"
  instance  = google_sql_database_instance.dolfin_database_instance.name
  host      = "%"
  password  = "Kess is 2 cool!"
}
