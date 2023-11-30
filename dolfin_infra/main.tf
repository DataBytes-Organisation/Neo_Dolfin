terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.51.0"
    }
  }
  backend "gcs" {
    bucket  = "dolfin"
    prefix  = "terraform-state"
  }
}

provider "google" {
  credentials = file(var.credentials_file)

  project = var.gcp_project_id
  region  = var.region
  zone    = var.zone
}

data "terraform_remote_state" "dolfin" {
  backend = "gcs"
  config = {
    bucket  = "dolfin"
    prefix  = "terraform-state"
  }
}

module "network" {
  source        = "./modules/network"
  project_name  = var.project_name
  region        = var.region
}

module "database" {
  source                = "./modules/database"
  region                = var.region
  project_name          = var.project_name
  vpc_network_self_link = module.network.vpc_network_self_link
}

module "compute" {
  source        = "./modules/compute"
  network_id    = module.network.vpc_network_id
  subnet_id     = module.network.vpc_subnet_id
  project_name  = var.project_name
}

