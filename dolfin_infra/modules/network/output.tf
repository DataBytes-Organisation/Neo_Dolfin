output "vpc_network_name" {
  value = google_compute_network.vpc_network.name
}
output "vpc_network_id" {
  value = google_compute_network.vpc_network.id
}
output "vpc_network_self_link" {
  value = google_compute_network.vpc_network.self_link
}
output "vpc_subnet_name" {
  value = google_compute_subnetwork.vpc_subnet.name
}
output "vpc_subnet_id" {
  value = google_compute_subnetwork.vpc_subnet.id
}