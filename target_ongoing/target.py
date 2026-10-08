"""Ongoing target class."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th
from hotglue_singer_sdk.target_sdk.target import TargetHotglue
from target_ongoing.sinks import ItemsSink, PurchaseOrdersSink


class TargetOngoing(TargetHotglue):
    """Target for Ongoing."""

    name = "target-ongoing"
    SINK_TYPES = [ItemsSink, PurchaseOrdersSink]

    config_jsonschema = th.PropertiesList(
        th.Property(
            "username",
            th.StringType(),
            required=True,
            description="Username for HTTP Basic authentication",
        ),
        th.Property(
            "password",
            th.StringType(),
            required=True,
            description="Password for HTTP Basic authentication",
        ),
        th.Property(
            "warehouse_name",
            th.StringType(),
            required=True,
            description="Ongoing WMS warehouse name in the API URL",
        ),
        th.Property(
            "goods_owner_id",
            th.IntegerType(),
            required=True,
            description="Ongoing WMS goods-owner identifier",
        ),
        th.Property(
            "warehouse_id",
            th.IntegerType(),
            required=True,
            description="Ongoing warehouse identifier for purchase orders",
        ),
        th.Property(
            "api_server",
            th.StringType(),
            default="api",
            description="Ongoing API server subdomain",
        ),
    ).to_dict()


if __name__ == "__main__":
    TargetOngoing.cli()
