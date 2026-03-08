"""
FruitQ FastAPI application.

Endpoints
---------
POST   /predict             Upload an image, get ripeness result + adds to inventory
GET    /inventory           List all fruits ranked by ripeness
DELETE /inventory/{id}      Remove a fruit (after it ships)
GET    /inventory/summary   High-level counts and ship-today list
GET    /health              Health check
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import mlflow_tracking
from src.inventory import get_inventory
from src.model import get_model

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up the model on startup so the first request isn't slow
    logger.info("Warming up model …")
    get_model()._load()
    yield


app = FastAPI(
    title="FruitQ",
    description="AI-powered fruit ripeness detection & shipping optimisation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "service": "fruitq"}


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

@app.post("/predict", tags=["prediction"])
async def predict(
    file: UploadFile = File(..., description="Fruit image (JPEG/PNG)"),
    fruit_name: str = Form("unknown", description="Optional fruit name / label"),
):
    """
    Upload a fruit image.  
    Returns the ripeness label, confidence score and shipping priority,
    and registers the fruit in the inventory.
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=415,
            detail="Unsupported media type. Please upload a JPEG or PNG image.",
        )

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = get_model().predict_from_bytes(data)
    except Exception as exc:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=500, detail=f"Model error: {exc}") from exc

    inventory = get_inventory()
    item = inventory.add(
        name=fruit_name,
        result=result,
        image_filename=file.filename,
    )

    # Fire-and-forget MLflow logging (errors are non-fatal)
    try:
        run_id = mlflow_tracking.log_prediction(
            image_filename=file.filename or "unknown",
            fruit_name=fruit_name,
            ripeness_label=result.label,
            confidence=result.confidence,
            shipping_priority=result.shipping_priority,
            raw_scores=result.raw_scores,
        )
    except Exception:
        logger.warning("MLflow logging failed", exc_info=True)
        run_id = None

    return {
        "item_id": item.id,
        "fruit_name": fruit_name,
        "ripeness_label": result.label,
        "confidence": result.confidence,
        "shipping_priority": result.shipping_priority,
        "raw_scores": result.raw_scores,
        "mlflow_run_id": run_id,
    }


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@app.get("/inventory", tags=["inventory"])
def get_inventory_list():
    """Return all fruits sorted by ripeness (most urgent first)."""
    items = get_inventory().get_all()
    return {"count": len(items), "fruits": [i.to_dict() for i in items]}


@app.get("/inventory/summary", tags=["inventory"])
def get_inventory_summary():
    """Return counts by ripeness category and the ship-today list."""
    return get_inventory().summary()


@app.delete("/inventory/{item_id}", tags=["inventory"])
def delete_fruit(item_id: str):
    """Remove a fruit from inventory (call this after it ships)."""
    removed = get_inventory().remove(item_id)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Fruit {item_id} not found.")
    return {"removed": item_id}
