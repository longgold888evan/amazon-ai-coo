from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from amazon_ai_coo.connectors.base import DataConnector
from amazon_ai_coo.domain.models import SellerState


_REGISTRY_PATH = Path(__file__).with_name("sellersprite_registry.json")


@lru_cache(maxsize=1)
def load_sellersprite_registry() -> dict[str, Any]:
    """Load the verified SellerSprite MCP capability registry.

    The registry is intentionally local and version-controlled so the orchestrator and
    coding agents share one stable description of SellerSprite's current tool surface.
    Runtime MCP tool discovery should still be treated as the final compatibility check.
    """

    with _REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_sellersprite_tool(tool_code: str) -> dict[str, Any]:
    """Return one SellerSprite tool definition by MCP code."""

    for tool in load_sellersprite_registry()["tools"]:
        if tool["code"] == tool_code:
            return tool
    raise KeyError(f"Unknown SellerSprite MCP tool: {tool_code}")


def list_sellersprite_tools(category: str | None = None) -> list[dict[str, Any]]:
    """List all known tools, optionally filtered by registry category."""

    tools = load_sellersprite_registry()["tools"]
    if category is None:
        return list(tools)
    return [tool for tool in tools if tool["category"] == category]


def should_prefer_amazon_first(*, seller_owned_fact: bool, amazon_equivalent_available: bool) -> bool:
    """Enforce the project's source-of-truth hierarchy.

    SellerSprite is an external market-intelligence source. If a fact belongs to our
    seller account and Amazon exposes the same fact through Ads API, SP-API, Brand
    Analytics, seller reports or another first-party surface, Amazon must be queried
    first and remains canonical on conflict.
    """

    return seller_owned_fact and amazon_equivalent_available


class SellerSpriteConnector(DataConnector):
    """SellerSprite market-intelligence boundary.

    Intended inputs include competitor ASIN trends, traffic keywords, keyword demand,
    ABA-derived research, review intelligence, market concentration and external trend
    signals exposed through SellerSprite's MCP/API surface.

    Routing contract:
    - Amazon first-party APIs are authoritative for equivalent seller-owned facts.
    - SellerSprite supplements first-party state with external market intelligence.
    - Conflicting third-party estimates are retained as benchmarks, not replacements.
    - SellerSprite is observe-only: it cannot authorize destructive Amazon writes.

    See ``docs/data_sources/SELLERSPRITE_MCP.md`` and
    ``sellersprite_registry.json`` for the verified 45-tool catalog and routing map.
    """

    name = "sellersprite"

    @property
    def registry(self) -> dict[str, Any]:
        return load_sellersprite_registry()

    async def enrich_state(self, state: SellerState) -> SellerState:
        return state
