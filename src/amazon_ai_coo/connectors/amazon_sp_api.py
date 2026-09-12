from __future__ import annotations

from amazon_ai_coo.connectors.base import DataConnector, WriteConnector
from amazon_ai_coo.domain.models import SellerState


class AmazonSPAPIConnector(DataConnector, WriteConnector):
    """Selling Partner API adapter boundary.

    Planned read scope:
    - orders / sales
    - FBA inventory
    - listings / catalog
    - product pricing / Featured Offer signals
    - finance / fees
    - Brand Analytics and other report-driven first-party metrics

    Planned write scope is added capability-by-capability after explicit validation;
    Seller Central UI availability must never be assumed to imply public API support.
    """

    name = "amazon_sp_api"

    async def enrich_state(self, state: SellerState) -> SellerState:
        return state

    async def execute(self, action_type: str, target: dict, parameters: dict) -> dict:
        raise RuntimeError("SP-API writes are disabled until capability-specific validation is complete")
