output "web_server_url" {
    value = join("",["http://",google_compute_instance.vm_instance.network_interface.0.access_config.0.nat_ip,":5000"])
}