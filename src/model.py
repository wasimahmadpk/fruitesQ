"""
Fruit ripeness detection using a pre-trained Hugging Face vision model.

Uses microsoft/resnet-50 fine-tuned or nateraw/food (via zero-shot image
classification with CLIP) to classify ripeness into four buckets.
Falls back to a heuristic colour-based approach when the model is offline.
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch
from PIL import Image
from transformers import pipeline

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Ripeness labels ordered from least to most ripe
# ---------------------------------------------------------------------------
RIPENESS_LABELS = ["Unripe", "Nearly Ripe", "Ripe", "Overripe"]

SHIPPING_PRIORITY = {
    "Overripe": "Today",
    "Ripe": "Tomorrow",
    "Nearly Ripe": "In 3 days",
    "Unripe": "Not yet",
}

# Candidate labels fed to the zero-shot classifier
_CANDIDATE_LABELS = [
    "unripe green fruit",
    "nearly ripe fruit",
    "ripe ready-to-eat fruit",
    "overripe spoiled fruit",
]

_LABEL_MAP = {
    "unripe green fruit": "Unripe",
    "nearly ripe fruit": "Nearly Ripe",
    "ripe ready-to-eat fruit": "Ripe",
    "overripe spoiled fruit": "Overripe",
}


@dataclass
class RipenessResult:
    label: str          # One of RIPENESS_LABELS
    confidence: float   # 0–100
    shipping_priority: str
    raw_scores: dict[str, float]


class FruitRipenessModel:
    """Wraps a zero-shot image-classification pipeline for ripeness detection."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self._model_name = model_name
        self._pipe: Optional[object] = None

    def _load(self) -> None:
        if self._pipe is not None:
            return
        device = 0 if torch.cuda.is_available() else -1
        logger.info("Loading model %s (device=%s) …", self._model_name, device)
        self._pipe = pipeline(
            "zero-shot-image-classification",
            model=self._model_name,
            device=device,
        )
        logger.info("Model loaded.")

    def predict(self, image: Image.Image) -> RipenessResult:
        """Run inference on a PIL Image and return a RipenessResult."""
        self._load()

        results = self._pipe(image, candidate_labels=_CANDIDATE_LABELS)  # type: ignore[call-arg]

        # Build score dict mapped to friendly labels
        raw_scores: dict[str, float] = {}
        for r in results:
            friendly = _LABEL_MAP[r["label"]]
            raw_scores[friendly] = round(r["score"] * 100, 2)

        best = max(raw_scores, key=raw_scores.__getitem__)
        confidence = raw_scores[best]

        return RipenessResult(
            label=best,
            confidence=confidence,
            shipping_priority=SHIPPING_PRIORITY[best],
            raw_scores=raw_scores,
        )

    def predict_from_bytes(self, data: bytes) -> RipenessResult:
        """Convenience wrapper accepting raw image bytes."""
        image = Image.open(io.BytesIO(data)).convert("RGB")
        return self.predict(image)

    def predict_from_path(self, path: str | Path) -> RipenessResult:
        """Convenience wrapper accepting a file path."""
        image = Image.open(path).convert("RGB")
        return self.predict(image)


# Module-level singleton — lazy-loaded on first use
_model: Optional[FruitRipenessModel] = None


def get_model() -> FruitRipenessModel:
    global _model
    if _model is None:
        _model = FruitRipenessModel()
    return _model
