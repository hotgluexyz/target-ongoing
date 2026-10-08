"""HTTP client and sink base classes for Ongoing."""

from __future__ import annotations
from typing import Any


from hotglue_singer_sdk.target_sdk.auth import BasicAuthenticator
from hotglue_singer_sdk.target_sdk.client import HotglueBaseSink, HotglueSink


class OngoingSink(HotglueBaseSink):
    """Ongoing Base target sink class for sinks."""

    @property
    def base_url(self) -> str:
        """Build the per-warehouse Ongoing Goods Owner REST API URL."""
        return (
            f"https://{self.config.get('api_server', 'api')}.ongoingsystems.se/"
            f"{self.config['warehouse_name']}/api/v1"
        )

    @property
    def authenticator(self) -> Any:
        return BasicAuthenticator(
            self._target,
            username=self.config.get("username"),
            password=self.config.get("password"),
        )


class OngoingRecordSink(OngoingSink, HotglueSink):
    """Ongoing Record target sink class for record sinks."""

    name = "OngoingRecordSink"

    def upsert_record(self, record: dict, _context: dict) -> None:
        """Upsert a record using Ongoing's idempotent PUT endpoints."""
        response = self.request_api("PUT", self.endpoint, request_data=record)
        body = response.json()
        record_id = body.get("articleSystemId") or body.get("purchaseOrderId")
        return record_id, True, {"updated": True}
