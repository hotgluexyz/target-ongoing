"""Ongoing target sink class, which handles writing streams."""

from __future__ import annotations

from target_ongoing.mapper import item_to_article, purchase_order_to_ongoing
from target_ongoing.client import OngoingRecordSink


class ItemsSink(OngoingRecordSink):
    """Upsert QuickBooks products as Ongoing articles."""

    name = "Items"
    endpoint = "/articles"

    def preprocess_record(self, record: dict, _context: dict) -> dict:
        """Map a QuickBooks product to the Ongoing article model."""
        return item_to_article(record, self.config["goods_owner_id"])


class PurchaseOrdersSink(OngoingRecordSink):
    """Upsert QuickBooks purchase orders in Ongoing."""

    name = "PurchaseOrders"
    endpoint = "/purchaseOrders"

    def preprocess_record(self, record: dict, _context: dict) -> dict:
        """Map a QuickBooks purchase order to the Ongoing API model."""
        return purchase_order_to_ongoing(
            record, self.config["goods_owner_id"], self.config["warehouse_id"]
        )
