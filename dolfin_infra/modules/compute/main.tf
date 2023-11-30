resource "google_compute_instance" "vm_instance" {
  name         = "${var.project_name}-vm"
  machine_type = "f1-micro"
  tags         = ["flask", "ssh"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  # Install Flask
  metadata_startup_script = "sudo apt-get update; sudo apt-get install -yq build-essential python3-pip rsync; pip install flask"

  network_interface {
    subnetwork = var.subnet_id
    access_config {}
  }
}

resource "google_compute_firewall" "ssh" {
  name = "allow-ssh"
  allow {
      ports    = ["22"]
      protocol = "tcp"
  }
  direction     = "INGRESS"
  network       = var.network_id
  priority      = 1000
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh"]
}