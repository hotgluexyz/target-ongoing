"""Tests standard target features using the built-in SDK tests library."""

from __future__ import annotations

import pytest

from target_ongoing.mapper import item_to_article, purchase_order_to_ongoing


def test_item_uses_name_for_article_number_and_preserves_sku() -> None:
    """Purchase-order references use item names, not optional SKUs."""
    article = item_to_article(
        {
            "Name": "Widget Blue",
            "Sku": "WID-BLU",
            "Type": "Inventory",
            "Active": False,
            "PurchaseCost": 4.5,
            "UnitPrice": 9.99,
        },
        42,
    )

    assert article == {
        "goodsOwnerId": 42,
        "articleNumber": "Widget Blue",
        "articleName": "Widget Blue",
        "productCode": "WID-BLU",
        "description": None,
        "isActive": False,
        "isStockArticle": True,
        "purchasePrice": 4.5,
        "customerPrice": 9.99,
    }


def test_purchase_order_maps_only_item_lines() -> None:
    """Description-only QuickBooks lines must not become invalid Ongoing rows."""
    purchase_order = purchase_order_to_ongoing(
        {
            "DocNumber": "PO-100",
            "TxnDate": "2026-10-08",
            "VendorRef": {"name": "Acme Supplies"},
            "Line": [
                {"Description": "Receiving instructions"},
                {
                    "Description": "Blue widgets",
                    "ItemBasedExpenseLineDetail": {
                        "ItemRef": {"name": "Widget Blue"},
                        "Qty": 3,
                        "UnitPrice": 4.5,
                    },
                },
            ],
        },
        42,
        2,
    )

    assert purchase_order == {
        "goodsOwnerId": 42,
        "purchaseOrderNumber": "PO-100",
        "warehouseId": 2,
        "supplierOrderNumber": None,
        "inDate": "2026-10-08",
        "supplierInfo": {"supplierName": "Acme Supplies"},
        "purchaseOrderLines": [
            {
                "rowNumber": "2",
                "articleNumber": "Widget Blue",
                "numberOfItems": 3,
                "rowPrice": 4.5,
                "comment": "Blue widgets",
            }
        ],
    }


def test_purchase_order_rejects_lines_without_products() -> None:
    """Avoid creating a purchase order that discards all source line items."""
    with pytest.raises(ValueError, match="no item-based lines"):
        purchase_order_to_ongoing({"DocNumber": "PO-101", "Line": [{"Description": "Note"}]}, 42, 2)
