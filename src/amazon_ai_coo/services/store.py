from __future__ import annotations

from copy import deepcopy

from amazon_ai_coo.domain.models import ActionProposal, SellerState


class InMemoryStore:
    """V0 persistence boundary.

    Keep the interface intentionally small so Postgres can replace this class
    without changing the API or decision engine contracts.
    """

    def __init__(self) -> None:
        self._states: dict[str, SellerState] = {}
        self._actions: dict[str, ActionProposal] = {}

    def get_state(self, asin: str) -> SellerState | None:
        state = self._states.get(asin)
        return deepcopy(state) if state else None

    def put_state(self, state: SellerState) -> SellerState:
        self._states[state.identity.asin] = deepcopy(state)
        return deepcopy(state)

    def put_action(self, action: ActionProposal) -> ActionProposal:
        self._actions[action.id] = deepcopy(action)
        return deepcopy(action)

    def get_action(self, action_id: str) -> ActionProposal | None:
        action = self._actions.get(action_id)
        return deepcopy(action) if action else None


store = InMemoryStore()
