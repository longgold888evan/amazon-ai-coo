from __future__ import annotations

from amazon_ai_coo.connectors.base import DataConnector
from amazon_ai_coo.domain.models import SellerState


class SellerSpriteConnector(DataConnector):
    """SellerSprite market-intelligence boundary.

    Intended inputs include competitor ASIN trends, traffic keywords, keyword demand,
    ABA-derived research, review intelligence, market concentration and external trend
    signals exposed through SellerSprite's MCP/API surface.

    This connector is observe-only by design. Its estimates may create hypotheses and
    recommendations, but cannot directly authorize destructive Amazon writes.
    """

    name = "sellersprite"

    async def enrich_state(self, state: SellerState) -> SellerState:
        return state
