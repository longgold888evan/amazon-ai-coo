from __future__ import annotations

from amazon_ai_coo.connectors.base import DataConnector, WriteConnector
from amazon_ai_coo.domain.models import SellerState


class AmazonAdsConnector(DataConnector, WriteConnector):
    """Amazon Ads adapter boundary.

    Planned read scope:
    - campaign/ad-group/target metadata
    - search-term, targeting, advertised-product and placement reports
    - campaign budget/bid state
    - Marketing Stream can later feed near-real-time event aggregates separately

    Planned write scope:
    - bid/budget updates
    - pause/enable
    - exact harvesting
    - negative keywords/targets

    Authentication and report polling are intentionally not implemented until
    account credentials are configured.
    """

    name = "amazon_ads"

    async def enrich_state(self, state: SellerState) -> SellerState:
        return state

    async def execute(self, action_type: str, target: dict, parameters: dict) -> dict:
        raise RuntimeError("Amazon Ads writes are disabled until credentials and idempotency are configured")
