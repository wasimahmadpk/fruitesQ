"""
MLflow tracking helpers.

Call log_prediction() after every inference to record inputs and outputs.
The MLflow tracking URI defaults to a local ./mlruns directory so no
external server is needed during development.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime

import mlflow

logger = logging.getLogger(__name__)

EXPERIMENT_NAME = "fruitq-ripeness-detection"
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "mlruns")

_initialized = False


def _init() -> None:
    global _initialized
    if _initialized:
        return
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    _initialized = True
    logger.info("MLflow tracking initialised. URI=%s", TRACKING_URI)


def log_prediction(
    image_filename: str,
    fruit_name: str,
    ripeness_label: str,
    confidence: float,
    shipping_priority: str,
    raw_scores: dict[str, float],
) -> str:
    """Log a single prediction as an MLflow run. Returns the run_id."""
    _init()
    with mlflow.start_run(run_name=f"predict-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}") as run:
        mlflow.log_param("image_filename", image_filename)
        mlflow.log_param("fruit_name", fruit_name)
        mlflow.log_param("ripeness_label", ripeness_label)
        mlflow.log_param("shipping_priority", shipping_priority)

        mlflow.log_metric("confidence", confidence)
        for label, score in raw_scores.items():
            mlflow.log_metric(f"score_{label.lower().replace(' ', '_')}", score)

        if confidence < 60:
            logger.warning(
                "Low confidence prediction! fruit=%s label=%s confidence=%.1f%%",
                fruit_name,
                ripeness_label,
                confidence,
            )
            mlflow.set_tag("alert", "low_confidence")

        return run.info.run_id


def get_experiment_url() -> str:
    """Return a human-readable URL to the MLflow UI (local by default)."""
    return "http://localhost:5000"
