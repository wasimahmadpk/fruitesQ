"""Unit tests for inventory.py."""

import pytest

from src.inventory import FruitInventory
from src.model import RipenessResult, SHIPPING_PRIORITY


def _make_result(label: str, confidence: float = 90.0) -> RipenessResult:
    raw = {"Unripe": 0, "Nearly Ripe": 0, "Ripe": 0, "Overripe": 0}
    raw[label] = confidence
    return RipenessResult(
        label=label,
        confidence=confidence,
        shipping_priority=SHIPPING_PRIORITY[label],
        raw_scores=raw,
    )


class TestFruitInventory:
    def setup_method(self):
        self.inv = FruitInventory()

    def test_add_returns_item(self):
        item = self.inv.add("Mango", _make_result("Ripe"))
        assert item.name == "Mango"
        assert item.ripeness_label == "Ripe"
        assert item.id

    def test_inventory_sorted_most_ripe_first(self):
        self.inv.add("Banana", _make_result("Unripe"))
        self.inv.add("Mango", _make_result("Overripe"))
        self.inv.add("Apple", _make_result("Nearly Ripe"))

        fruits = self.inv.get_all()
        labels = [f.ripeness_label for f in fruits]
        assert labels == ["Overripe", "Nearly Ripe", "Unripe"]

    def test_remove_existing(self):
        item = self.inv.add("Pear", _make_result("Ripe"))
        removed = self.inv.remove(item.id)
        assert removed is True
        assert self.inv.get(item.id) is None

    def test_remove_nonexistent_returns_false(self):
        assert self.inv.remove("nonexistent-id") is False

    def test_summary_counts(self):
        self.inv.add("A", _make_result("Ripe"))
        self.inv.add("B", _make_result("Ripe"))
        self.inv.add("C", _make_result("Overripe"))

        s = self.inv.summary()
        assert s["total"] == 3
        assert s["by_ripeness"]["Ripe"] == 2
        assert s["by_ripeness"]["Overripe"] == 1
        assert len(s["ship_today"]) == 1

    def test_clear(self):
        self.inv.add("X", _make_result("Ripe"))
        self.inv.clear()
        assert self.inv.get_all() == []

    def test_ripeness_rank_ordering(self):
        item_unripe = self.inv.add("U", _make_result("Unripe"))
        item_overripe = self.inv.add("O", _make_result("Overripe"))
        assert item_overripe.ripeness_rank > item_unripe.ripeness_rank
