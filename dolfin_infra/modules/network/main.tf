resource "google_compute_network" "vpc_network" {
  name                    = "${var.project_name}-network"
  auto_create_subnetworks = false
  mtu                     = 1460
}

resource "google_compute_subnetwork" "vpc_subnet" {
  name          = "${var.project_name}-vpc-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.self_link
}

resource "google_compute_global_address" "ip_range" {
  name          = "${var.project_name}-ip-addresses"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

resource "google_service_networking_connection" "vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.ip_range.name]
}