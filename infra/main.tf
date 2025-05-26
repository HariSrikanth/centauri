terraform {
  required_version = ">= 1.0.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "alpha-me-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "alpha-me-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "alpha-me-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.vpc.id
  region        = var.region

  private_ip_google_access = true
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "postgres" {
  name             = "alpha-me-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro"  # Smallest instance, adjust as needed
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
    }
    backup_configuration {
      enabled = true
      point_in_time_recovery_enabled = true
    }
  }

  deletion_protection = true
}

resource "google_sql_database" "database" {
  name     = "alpha_me"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "user" {
  name     = "alpha_me"
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Redis (Memorystore)
resource "google_redis_instance" "redis" {
  name           = "alpha-me-redis"
  memory_size_gb = 1
  region         = var.region

  authorized_network = google_compute_network.vpc.id
  redis_version     = "REDIS_7_0"
  tier             = "BASIC"
}

# Cloud Storage
resource "google_storage_bucket" "newsletters" {
  name          = "alpha-me-newsletters"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

# Secret Manager
resource "google_secret_manager_secret" "secrets" {
  for_each = toset([
    "clerk-secret-key",
    "openai-api-key",
    "github-client-id",
    "github-client-secret",
    "twitter-api-key",
    "twitter-api-secret"
  ])

  secret_id = "alpha-me-${each.key}"

  replication {
    auto {}
  }
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run" {
  account_id   = "alpha-me-cloud-run"
  display_name = "Alpha.me Cloud Run Service Account"
}

# IAM permissions
resource "google_project_iam_member" "cloud_run_sa" {
  for_each = toset([
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectViewer",
    "roles/cloudsql.client",
    "roles/redis.viewer"
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Run (API)
resource "google_cloud_run_service" "api" {
  name     = "alpha-me-api"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      containers {
        image = "gcr.io/${var.project_id}/alpha-me-api:latest"
        ports {
          container_port = 8080
          name = "http1"
        }
        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DATABASE_URL"
          value = "postgresql+asyncpg://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.database.name}"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run (Worker)
resource "google_cloud_run_service" "worker" {
  name     = "alpha-me-worker"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      containers {
        image = "gcr.io/${var.project_id}/alpha-me-worker:latest"
        ports {
          container_port = 8080
          name = "http1"
        }
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }
        env {
          name  = "ENVIRONMENT"
          value = "production"
        }
        env {
          name  = "DATABASE_URL"
          value = "postgresql+asyncpg://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.database.name}"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.redis.host}:${google_redis_instance.redis.port}/0"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Outputs
output "api_url" {
  value = google_cloud_run_service.api.status[0].url
}

output "database_private_ip" {
  value = google_sql_database_instance.postgres.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.redis.host
}

output "storage_bucket" {
  value = google_storage_bucket.newsletters.name
} 