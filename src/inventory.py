"""
In-memory fruit inventory with ripeness-based ranking.

Each fruit entry stores its name, ripeness label, confidence score and
shipping priority. The inventory is sorted so the most ripe fruits
(highest urgency) always appear first.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import List, Optional

from src.model import RIPENESS_LABELS, SHIPPING_PRIORITY, RipenessResult

# Higher index = more ripe = higher shipping urgency
_RIPENESS_RANK = {label: idx for idx, label in enumerate(RIPENESS_LABELS)}


@dataclass
class FruitItem:
    id: str
    name: str
    ripeness_label: str
    confidence: float
    shipping_priority: str
    added_at: datetime = field(default_factory=datetime.utcnow)
    image_filename: Optional[str] = None

    @property
    def ripeness_rank(self) -> int:
        return _RIPENESS_RANK.get(self.ripeness_label, 0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "ripeness_label": self.ripeness_label,
            "confidence": self.confidence,
            "shipping_priority": self.shipping_priority,
            "ripeness_rank": self.ripeness_rank,
            "added_at": self.added_at.isoformat(),
            "image_filename": self.image_filename,
        }


class FruitInventory:
    """Thread-safe in-memory inventory sorted by descending ripeness."""

    def __init__(self) -> None:
        self._items: List[FruitItem] = []
        self._lock = Lock()

    def add(
        self,
        name: str,
        result: RipenessResult,
        image_filename: Optional[str] = None,
    ) -> FruitItem:
        item = FruitItem(
            id=str(uuid.uuid4()),
            name=name,
            ripeness_label=result.label,
            confidence=result.confidence,
            shipping_priority=result.shipping_priority,
            image_filename=image_filename,
        )
        with self._lock:
            self._items.append(item)
            self._sort()
        return item

    def get_all(self) -> List[FruitItem]:
        with self._lock:
            return list(self._items)

    def get(self, item_id: str) -> Optional[FruitItem]:
        with self._lock:
            return next((i for i in self._items if i.id == item_id), None)

    def remove(self, item_id: str) -> bool:
        with self._lock:
            before = len(self._items)
            self._items = [i for i in self._items if i.id != item_id]
            return len(self._items) < before

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def _sort(self) -> None:
        """Sort descending by ripeness rank (most ripe first)."""
        self._items.sort(key=lambda x: x.ripeness_rank, reverse=True)

    def summary(self) -> dict:
        items = self.get_all()
        counts: dict[str, int] = {label: 0 for label in RIPENESS_LABELS}
        for item in items:
            counts[item.ripeness_label] += 1
        ship_today = [i.to_dict() for i in items if i.shipping_priority == "Today"]
        return {
            "total": len(items),
            "by_ripeness": counts,
            "ship_today": ship_today,
        }


# Module-level singleton
_inventory = FruitInventory()


def get_inventory() -> FruitInventory:
    return _inventory
