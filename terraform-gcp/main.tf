# FruitQ - Google Cloud Run deployment
# Uses Artifact Registry for the container image (pushed by CI).

terraform {
  backend "gcs" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Variables ─────────────────────────────────────────────────────────────────

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region (e.g. us-central1)"
  type        = string
  default     = "us-central1"
}

variable "image_tag" {
  description = "Docker image tag (e.g. latest or git SHA)"
  type        = string
  default     = "latest"
}

locals {
  app_name   = "fruitq"
  image_name = "${var.region}-docker.pkg.dev/${var.project_id}/${local.app_name}/api:${var.image_tag}"
}

# APIs (Artifact Registry, Cloud Run) must be enabled in the console or by a user
# with Service Usage Admin. The Artifact Registry repo is created by CI (gcloud).
# Terraform only creates the two Cloud Run services and IAM.

# ── Cloud Run: API ───────────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "api" {
  name     = "${local.app_name}-api"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = local.image_name

      ports {
        container_port = 8000
      }

      env {
        name  = "MLFLOW_TRACKING_URI"
        value = "mlruns"
      }
      env {
        name  = "SKIP_MODEL_WARMUP"
        value = "1"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
        cpu_idle = true
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }

    timeout = "600s"
  }

}

# Allow unauthenticated access (public API)
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  location = google_cloud_run_v2_service.api.location
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Cloud Run: Dashboard ─────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "dashboard" {
  name     = "${local.app_name}-dashboard"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = local.image_name

      args = [
        "streamlit", "run", "src/dashboard.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
      ]

      ports {
        container_port = 8501
      }

      env {
        name  = "FRUITQ_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle = true
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }
  }

  depends_on = [
    google_cloud_run_v2_service.api,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "dashboard_public" {
  location = google_cloud_run_v2_service.dashboard.location
  name     = google_cloud_run_v2_service.dashboard.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Outputs ───────────────────────────────────────────────────────────────────

output "api_url" {
  description = "Public URL for the FruitQ REST API"
  value       = google_cloud_run_v2_service.api.uri
}

output "dashboard_url" {
  description = "Public URL for the Streamlit dashboard"
  value       = google_cloud_run_v2_service.dashboard.uri
}

output "artifact_registry" {
  description = "Artifact Registry image path (push your image here from CI)"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${local.app_name}/api"
}
