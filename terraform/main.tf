terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }

  # Uncomment to store state in Azure Blob Storage (recommended for teams)
  # backend "azurerm" {
  #   resource_group_name  = "fruitq-tfstate-rg"
  #   storage_account_name = "fruitqtfstate"
  #   container_name       = "tfstate"
  #   key                  = "prod.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {}
}

# ── Variables ─────────────────────────────────────────────────────────────────

variable "location" {
  description = "Azure region"
  default     = "eastus"
}

variable "image_tag" {
  description = "Docker image tag (git SHA)"
  default     = "latest"
}

variable "registry_username" {
  description = "GHCR username"
}

variable "registry_password" {
  description = "GHCR PAT or GITHUB_TOKEN"
  sensitive   = true
}

locals {
  app_name = "fruitq"
  rg_name  = "${local.app_name}-rg"
  image    = "ghcr.io/wasimahmadpk/fruitesq:${var.image_tag}"
}

# ── Resource Group ────────────────────────────────────────────────────────────

resource "azurerm_resource_group" "main" {
  name     = local.rg_name
  location = var.location

  tags = {
    project = local.app_name
  }
}

# ── Log Analytics (optional monitoring) ───────────────────────────────────────

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.app_name}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# ── Container Group ───────────────────────────────────────────────────────────

resource "azurerm_container_group" "api" {
  name                = "${local.app_name}-api"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = "${local.app_name}-api"
  os_type             = "Linux"

  image_registry_credential {
    server   = "ghcr.io"
    username = var.registry_username
    password = var.registry_password
  }

  container {
    name   = "fruitq-api"
    image  = local.image
    cpu    = "1"
    memory = "2"

    ports {
      port     = 8000
      protocol = "TCP"
    }

    environment_variables = {
      MLFLOW_TRACKING_URI = "mlruns"
    }
  }

  tags = {
    project = local.app_name
  }
}

resource "azurerm_container_group" "dashboard" {
  name                = "${local.app_name}-dashboard"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  ip_address_type     = "Public"
  dns_name_label      = "${local.app_name}-dashboard"
  os_type             = "Linux"

  image_registry_credential {
    server   = "ghcr.io"
    username = var.registry_username
    password = var.registry_password
  }

  container {
    name   = "fruitq-dashboard"
    image  = local.image
    cpu    = "0.5"
    memory = "1"

    ports {
      port     = 8501
      protocol = "TCP"
    }

    environment_variables = {
      FRUITQ_API_URL = "http://${azurerm_container_group.api.fqdn}:8000"
    }

    # Override default CMD to run Streamlit
    commands = [
      "streamlit", "run", "src/dashboard.py",
      "--server.port", "8501",
      "--server.address", "0.0.0.0",
    ]
  }

  tags = {
    project = local.app_name
  }
}

# ── Outputs ───────────────────────────────────────────────────────────────────

output "api_url" {
  description = "Public URL for the FruitQ REST API"
  value       = "http://${azurerm_container_group.api.fqdn}:8000"
}

output "dashboard_url" {
  description = "Public URL for the Streamlit dashboard"
  value       = "http://${azurerm_container_group.dashboard.fqdn}:8501"
}
