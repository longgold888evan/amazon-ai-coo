from __future__ import annotations

from dataclasses import dataclass

from amazon_ai_coo.domain.models import ActionProposal, ActionType, SellerState


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    reason: str


class GuardrailEngine:
    def __init__(
        self,
        max_bid_change_pct: float = 25.0,
        max_budget_change_pct: float = 30.0,
        min_contribution_margin_pct: float = 0.0,
    ) -> None:
        self.max_bid_change_pct = max_bid_change_pct
        self.max_budget_change_pct = max_budget_change_pct
        self.min_contribution_margin_pct = min_contribution_margin_pct

    def evaluate(self, action: ActionProposal, state: SellerState) -> GuardrailDecision:
        if action.action_type == ActionType.ADJUST_BID:
            change = abs(float(action.parameters.get("relative_change_pct", 0)))
            if change > self.max_bid_change_pct:
                return GuardrailDecision(False, "bid change exceeds configured maximum")

        if action.action_type == ActionType.ADJUST_BUDGET:
            change = abs(float(action.parameters.get("relative_change_pct", 0)))
            if change > self.max_budget_change_pct:
                return GuardrailDecision(False, "budget change exceeds configured maximum")

        if action.action_type == ActionType.ADJUST_PRICE:
            return GuardrailDecision(False, "price changes require simulation and explicit human approval in V0")

        if action.action_type == ActionType.UPDATE_LISTING:
            return GuardrailDecision(False, "listing writes are disabled in V0")

        margin = state.economics.get("contribution_margin_pct")
        if (
            margin
            and isinstance(margin.value, (int, float))
            and float(margin.value) < self.min_contribution_margin_pct
        ):
            return GuardrailDecision(False, "contribution margin is below configured floor")

        return GuardrailDecision(True, "passed V0 guardrails")
