"""
Integration tests for the FastAPI application.

The vision model is mocked so tests run instantly without GPU/internet access.
"""

from __future__ import annotations

import io
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.model import RipenessResult, SHIPPING_PRIORITY

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

MOCK_RESULT = RipenessResult(
    label="Ripe",
    confidence=87.5,
    shipping_priority=SHIPPING_PRIORITY["Ripe"],
    raw_scores={"Unripe": 2.0, "Nearly Ripe": 8.0, "Ripe": 87.5, "Overripe": 2.5},
)


def _make_png_bytes() -> bytes:
    """Create a tiny in-memory PNG for upload tests."""
    img = Image.new("RGB", (32, 32), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def client():
    # Patch model and MLflow before importing the app to avoid real I/O
    with (
        patch("src.api.get_model") as mock_get_model,
        patch("src.api.mlflow_tracking.log_prediction", return_value="fake-run-id"),
    ):
        mock_model = MagicMock()
        mock_model.predict_from_bytes.return_value = MOCK_RESULT
        mock_model._load = MagicMock()
        mock_get_model.return_value = mock_model

        from src.api import app
        from src.inventory import get_inventory

        # Reset inventory between tests
        get_inventory().clear()

        yield TestClient(app, raise_server_exceptions=True)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestPredict:
    def test_predict_success(self, client):
        png = _make_png_bytes()
        r = client.post(
            "/predict",
            files={"file": ("apple.png", png, "image/png")},
            data={"fruit_name": "apple"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["ripeness_label"] == "Ripe"
        assert body["confidence"] == 87.5
        assert body["shipping_priority"] == "Tomorrow"
        assert "item_id" in body

    def test_predict_unsupported_media(self, client):
        r = client.post(
            "/predict",
            files={"file": ("doc.pdf", b"%PDF", "application/pdf")},
            data={"fruit_name": "test"},
        )
        assert r.status_code == 415

    def test_predict_empty_file(self, client):
        r = client.post(
            "/predict",
            files={"file": ("empty.png", b"", "image/png")},
            data={"fruit_name": "test"},
        )
        assert r.status_code == 400


class TestInventory:
    def _add_fruit(self, client, name: str = "mango") -> str:
        png = _make_png_bytes()
        r = client.post(
            "/predict",
            files={"file": ("fruit.png", png, "image/png")},
            data={"fruit_name": name},
        )
        assert r.status_code == 200
        return r.json()["item_id"]

    def test_get_inventory_empty(self, client):
        r = client.get("/inventory")
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_get_inventory_after_predict(self, client):
        self._add_fruit(client, "mango")
        r = client.get("/inventory")
        assert r.status_code == 200
        assert r.json()["count"] == 1
        assert r.json()["fruits"][0]["name"] == "mango"

    def test_delete_fruit(self, client):
        item_id = self._add_fruit(client)
        r = client.delete(f"/inventory/{item_id}")
        assert r.status_code == 200
        assert r.json()["removed"] == item_id

        r2 = client.get("/inventory")
        assert r2.json()["count"] == 0

    def test_delete_nonexistent(self, client):
        r = client.delete("/inventory/does-not-exist")
        assert r.status_code == 404

    def test_inventory_summary(self, client):
        self._add_fruit(client, "apple")
        r = client.get("/inventory/summary")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert "by_ripeness" in body
