"""Map QuickBooks records to the Ongoing WMS REST API."""

from __future__ import annotations

import json
from typing import Any


def _first(*values: Any, default: Any = None) -> Any:  # noqa: ANN401
    """Return the first non-empty value."""
    return next((value for value in values if value not in (None, "")), default)


def _reference_name(reference: Any) -> str | None:  # noqa: ANN401
    """Return a display name from a QuickBooks reference."""
    if isinstance(reference, dict):
        return _first(reference.get("name"), reference.get("Name"))
    return reference


def _as_list(value: Any) -> list[Any]:  # noqa: ANN401
    """Decode arrays serialized by the Parquet-to-ETL handoff."""
    if isinstance(value, str):
        value = json.loads(value)
    return value if isinstance(value, list) else []


def item_to_article(record: dict[str, Any], goods_owner_id: int) -> dict[str, Any]:
    """Map a QuickBooks item to an idempotent Ongoing article payload."""
    name = _first(record.get("name"), record.get("Name"))
    if not name:
        message = "QuickBooks item is missing Name."
        raise ValueError(message)

    bill_item = record.get("billItem") or {}
    invoice_item = record.get("invoiceItem") or {}
    return {
        "goodsOwnerId": goods_owner_id,
        # Purchase-order ItemRef values use the QuickBooks item name, so it is
        # the only identifier that keeps product and purchase-order writes aligned.
        "articleNumber": name,
        "articleName": name,
        "productCode": _first(record.get("sku"), record.get("Sku")),
        "description": _first(
            record.get("description"),
            record.get("Description"),
            invoice_item.get("description"),
            invoice_item.get("Description"),
            bill_item.get("description"),
            bill_item.get("Description"),
        ),
        "isActive": _first(record.get("active"), record.get("Active"), default=True),
        "isStockArticle": _first(record.get("type"), record.get("Type")) == "Inventory",
        "purchasePrice": _first(
            record.get("purchaseCost"),
            record.get("PurchaseCost"),
            bill_item.get("unitPrice"),
            bill_item.get("UnitPrice"),
        ),
        "customerPrice": _first(
            record.get("unitPrice"),
            record.get("UnitPrice"),
            invoice_item.get("unitPrice"),
            invoice_item.get("UnitPrice"),
        ),
    }


def _line_to_purchase_order_line(line: dict[str, Any], index: int) -> dict[str, Any] | None:
    """Map either a unified or native QuickBooks purchase-order line."""
    detail = line.get("ItemBasedExpenseLineDetail") or {}
    article_number = _first(
        line.get("productName"),
        _reference_name(detail.get("ItemRef")),
    )
    if not article_number:
        return None

    return {
        "rowNumber": str(index),
        "articleNumber": article_number,
        "numberOfItems": _first(line.get("quantity"), line.get("Qty"), detail.get("Qty")),
        "rowPrice": _first(line.get("unitPrice"), line.get("UnitPrice"), detail.get("UnitPrice")),
        "comment": _first(line.get("description"), line.get("Description")),
    }


def purchase_order_to_ongoing(
    record: dict[str, Any], goods_owner_id: int, warehouse_id: int
) -> dict[str, Any]:
    """Map a QuickBooks purchase order to an Ongoing purchase-order payload."""
    number = _first(record.get("purchaseOrderNumber"), record.get("DocNumber"), record.get("Id"))
    if not number:
        message = "QuickBooks purchase order is missing DocNumber or Id."
        raise ValueError(message)

    lines = _as_list(record.get("lineItems") or record.get("Line"))
    payload_lines = []
    for index, line in enumerate(lines, start=1):
        mapped = _line_to_purchase_order_line(line, index)
        if mapped:
            payload_lines.append(mapped)
    if lines and not payload_lines:
        message = "QuickBooks purchase order has no item-based lines."
        raise ValueError(message)

    vendor = _first(record.get("vendorName"), _reference_name(record.get("VendorRef")))
    return {
        "goodsOwnerId": goods_owner_id,
        "purchaseOrderNumber": str(number),
        "warehouseId": warehouse_id,
        "supplierOrderNumber": _first(record.get("supplierOrderNumber"), record.get("PrivateNote")),
        "inDate": _first(record.get("inDate"), record.get("TxnDate")),
        "supplierInfo": {"supplierName": vendor} if vendor else None,
        "purchaseOrderLines": payload_lines,
    }
