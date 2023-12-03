resource "google_compute_instance" "vm_instance" {
  name         = "${var.project_name}-vm"
  machine_type = "f1-micro"
  tags         = ["allow-connections"]

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  network_interface {
    network = var.network_name
    subnetwork = var.subnet_name
    access_config {}
  }

  metadata = {
    gce-container-declaration = <<-EOT
    spec:
      containers:
        - name: dolfin-anomaly-detection
          image: gcr.io/${var.project_name}/dolfin-anomaly-detection
          ports:
            - containerPort: 5000
    EOT
  }

  service_account {
    scopes = ["cloud-platform"]
  }
}

resource "google_compute_firewall" "allow_connections" {
  name          = "allow-connections"
  network       = var.network_name
  direction     = "INGRESS"

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "5000", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["allow-connections"]
}