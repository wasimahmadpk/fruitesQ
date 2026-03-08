# 🍎 FruitQ

> AI-powered fruit ripeness detection & shipping optimisation.

Upload a photo of a fruit → AI detects its ripeness → System ranks all fruits in the inventory → Most ripe ships first.

### Dashboard

<p align="center">
  <img src="docs/dashboard_screenshot.png" alt="FruitQ Dashboard" width="700">
</p>

---

## Architecture

```
┌──────────────┐     POST /predict      ┌──────────────────────┐
│  Streamlit   │ ──────────────────────▶│  FastAPI  (api.py)   │
│  Dashboard   │ ◀────────────────────── │                      │
└──────────────┘   JSON result           │  model.py  (CLIP)    │
                                         │  inventory.py        │
                                         │  mlflow_tracking.py  │
                                         └──────────────────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │    MLflow UI     │
                                         │  (local ./mlruns)│
                                         └─────────────────┘
```

| Layer | Technology |
|---|---|
| Vision model | `openai/clip-vit-base-patch32` via Hugging Face Transformers |
| REST API | FastAPI + Uvicorn |
| Dashboard | Streamlit + Plotly |
| Experiment tracking | MLflow |
| Containerisation | Docker (multi-stage build) |
| CI/CD | GitHub Actions |
| Cloud deployment | Google Cloud Run (Terraform) or Azure Container Instances |

---

## Ripeness Labels

| Label | Shipping Priority |
|---|---|
| 🔴 Overripe | Today |
| 🟠 Ripe | Tomorrow |
| 🟡 Nearly Ripe | In 3 days |
| 🟢 Unripe | Not yet |

---

## Quick Start (Local)

### 1 — Clone & install

```bash
git clone https://github.com/wasimahmadpk/fruitesQ.git
cd fruitesQ
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2 — Start the API

```bash
uvicorn src.api:app --reload --port 8000
```

The first request will download the CLIP model (~340 MB) from Hugging Face automatically.

Interactive docs: http://localhost:8000/docs

### 3 — Start the Dashboard

```bash
streamlit run src/dashboard.py
```

Dashboard: http://localhost:8501

### 4 — Start MLflow UI (optional)

```bash
mlflow ui --port 5000
```

MLflow UI: http://localhost:5000

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/predict` | Upload image → get ripeness + add to inventory |
| `GET` | `/inventory` | List all fruits ranked by ripeness |
| `GET` | `/inventory/summary` | Counts by ripeness + ship-today list |
| `DELETE` | `/inventory/{id}` | Remove a fruit after it ships |
| `GET` | `/health` | Health check |

### Example — curl

```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/mango.jpg" \
  -F "fruit_name=mango"
```

Response:

```json
{
  "item_id": "3f4a...",
  "fruit_name": "mango",
  "ripeness_label": "Ripe",
  "confidence": 84.3,
  "shipping_priority": "Tomorrow",
  "raw_scores": {
    "Unripe": 3.1,
    "Nearly Ripe": 9.2,
    "Ripe": 84.3,
    "Overripe": 3.4
  },
  "mlflow_run_id": "abc123..."
}
```

---

## Docker

### Build & run locally

```bash
# API
docker build -t fruitq .
docker run -p 8000:8000 fruitq

# Dashboard (override CMD)
docker run -p 8501:8501 \
  -e FRUITQ_API_URL=http://host.docker.internal:8000 \
  fruitq \
  streamlit run src/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Compose (both services together)

```bash
docker compose up
```

---

## Running Tests

```bash
pytest tests/ -v
```

Tests mock the vision model so no GPU or internet access is required.

---

## CI/CD Pipeline

Every push triggers:

1. **Test** — `pytest tests/`
2. **Build** — Docker image built and pushed to GHCR (on `main` only)
3. **Deploy** — Image pushed to Google Artifact Registry and deployed to **Google Cloud Run** (on `main` only)

Required GitHub Secrets (for GCP deploy):

| Secret | Description |
|---|---|
| `GCP_PROJECT_ID` | Your GCP project ID (e.g. `my-fruitq-project`) |
| `GCP_SA_KEY` | Service account JSON key (full contents, for CI auth) |
| `GCP_REGION` | Region (e.g. `us-central1`) |

See [docs/GCP_SETUP.md](docs/GCP_SETUP.md) for step-by-step Google Cloud setup.

---

## Cloud Deployment

### Google Cloud (recommended)

```bash
cd terraform-gcp
terraform init
terraform apply -var="project_id=YOUR_GCP_PROJECT_ID" -var="region=us-central1"
```

Outputs: `api_url`, `dashboard_url`, `artifact_registry` (image path for CI).

### Azure (optional)

```bash
cd terraform
terraform init
terraform apply -var="registry_username=YOUR_GITHUB_USERNAME" -var="registry_password=YOUR_GHCR_PAT"
```

---

## MLflow Tracking

Every prediction logs:

- `image_filename` — uploaded file name
- `fruit_name` — fruit label
- `ripeness_label` — detected class
- `shipping_priority` — Today / Tomorrow / In 3 days / Not yet
- `confidence` — model confidence (0–100 %)
- Per-class scores

An `alert: low_confidence` tag is added when confidence drops below 60 %.

---

## Project Structure

```
fruitesQ/
├── src/
│   ├── api.py           # FastAPI endpoints
│   ├── model.py         # CLIP-based ripeness model
│   ├── inventory.py     # Ripeness ranking & inventory management
│   └── dashboard.py     # Streamlit dashboard
├── tests/
│   ├── test_api.py
│   └── test_inventory.py
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI/CD
├── terraform/
│   └── main.tf          # Azure Container Instances (optional)
├── terraform-gcp/
│   └── main.tf          # Google Cloud Run (Artifact Registry + 2 services)
├── mlflow_tracking.py   # MLflow helpers
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Interview Summary

> "I built FruitQ — an AI-powered fruit ripeness detection system. It uses a pre-trained CLIP vision model from Hugging Face to classify fruit ripeness into four categories and rank them so the most ripe ones ship first, reducing food waste. The system has a REST API built with FastAPI, a Streamlit dashboard with real-time inventory management and live camera capture, is fully containerised with Docker, deployed to Google Cloud Run using Terraform, and has a CI/CD pipeline with GitHub Actions. All predictions are tracked with MLflow, including low-confidence alerts."

---

## Total Cost

**$0** — all tools are free or have a free tier.
