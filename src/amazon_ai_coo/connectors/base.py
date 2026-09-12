from __future__ import annotations

from abc import ABC, abstractmethod

from amazon_ai_coo.domain.models import SellerState


class DataConnector(ABC):
    name: str

    @abstractmethod
    async def enrich_state(self, state: SellerState) -> SellerState:
        """Return a state enriched with fields owned by this connector."""
        raise NotImplementedError


class WriteConnector(ABC):
    name: str

    @abstractmethod
    async def execute(self, action_type: str, target: dict, parameters: dict) -> dict:
        raise NotImplementedError
