from __future__ import annotations

from datetime import UTC, datetime

from amazon_ai_coo.domain.models import (
    ActionProposal,
    ActionType,
    Confidence,
    Diagnosis,
    Evidence,
    GoalType,
    RecommendationBundle,
    RiskLevel,
    SellerState,
)


def _number(section: dict, key: str) -> float | None:
    metric = section.get(key)
    if metric is None or not isinstance(metric.value, (int, float)):
        return None
    return float(metric.value)


def _evidence(state: SellerState, section_name: str, key: str, note: str | None = None) -> Evidence | None:
    section = getattr(state, section_name)
    metric = section.get(key)
    if metric is None:
        return None
    return Evidence(
        field=f"{section_name}.{key}",
        value=metric.value,
        source=metric.source,
        observed_at=metric.observed_at,
        confidence=metric.confidence,
        note=note,
    )


def _goal(state: SellerState, goal_type: GoalType):
    return next((goal for goal in state.goals if goal.type == goal_type), None)


class DecisionEngine:
    """Deterministic V0 decision layer.

    Rules are intentionally explicit and auditable. LLM planning will later consume
    the same SellerState and produce proposals through the same ActionProposal contract.
    """

    def recommend(self, state: SellerState) -> RecommendationBundle:
        bundle = RecommendationBundle(asin=state.identity.asin)
        bundle = self._ads_economics_rules(state, bundle)
        bundle = self._inventory_goal_rules(state, bundle)
        bundle = self._market_context_rules(state, bundle)
        return bundle

    def _ads_economics_rules(self, state: SellerState, bundle: RecommendationBundle) -> RecommendationBundle:
        acos = _number(state.ads, "acos_7d")
        break_even_acos = _number(state.economics, "break_even_acos")
        budget_utilization = _number(state.ads, "budget_utilization_7d")

        if acos is not None and break_even_acos is not None and acos > break_even_acos:
            evidence = [
                item
                for item in (
                    _evidence(state, "ads", "acos_7d"),
                    _evidence(state, "economics", "break_even_acos"),
                )
                if item
            ]
            bundle.diagnoses.append(
                Diagnosis(
                    code="ADS_ABOVE_BREAK_EVEN",
                    summary="7-day ad cost ratio is above modeled break-even ACOS.",
                    confidence=Confidence.HIGH,
                    evidence=evidence,
                )
            )
            bundle.actions.append(
                ActionProposal(
                    action_type=ActionType.ADJUST_BID,
                    target={"scope": "underperforming_targets"},
                    parameters={"relative_change_pct": -10},
                    rationale="Reduce exposure on inefficient targets while preserving traffic for diagnosis.",
                    evidence=evidence,
                    confidence=Confidence.HIGH,
                    risk=RiskLevel.MEDIUM,
                    verification_plan={"window_hours": 72, "metrics": ["acos_7d", "sales_7d", "cvr_7d"]},
                )
            )

        if (
            acos is not None
            and break_even_acos is not None
            and budget_utilization is not None
            and acos < break_even_acos * 0.7
            and budget_utilization >= 0.9
        ):
            evidence = [
                item
                for item in (
                    _evidence(state, "ads", "acos_7d"),
                    _evidence(state, "economics", "break_even_acos"),
                    _evidence(state, "ads", "budget_utilization_7d"),
                )
                if item
            ]
            bundle.diagnoses.append(
                Diagnosis(
                    code="PROFITABLE_BUDGET_CONSTRAINED",
                    summary="Ads are well below break-even ACOS and are consuming most available budget.",
                    confidence=Confidence.HIGH,
                    evidence=evidence,
                )
            )
            bundle.actions.append(
                ActionProposal(
                    action_type=ActionType.ADJUST_BUDGET,
                    target={"scope": "profitable_budget_constrained_campaigns"},
                    parameters={"relative_change_pct": 15},
                    rationale="Expand profitable traffic without changing targeting semantics.",
                    evidence=evidence,
                    confidence=Confidence.HIGH,
                    risk=RiskLevel.LOW,
                    verification_plan={"window_hours": 72, "metrics": ["sales_7d", "acos_7d", "spend_7d"]},
                )
            )
        return bundle

    def _inventory_goal_rules(self, state: SellerState, bundle: RecommendationBundle) -> RecommendationBundle:
        clear_goal = _goal(state, GoalType.CLEAR_INVENTORY)
        days_of_supply = _number(state.inventory, "days_of_supply")
        contribution_margin_pct = _number(state.economics, "contribution_margin_pct")
        if clear_goal is None or clear_goal.deadline is None or days_of_supply is None:
            return bundle

        now = datetime.now(UTC)
        remaining_days = max((clear_goal.deadline - now).total_seconds() / 86400, 0)
        if days_of_supply > remaining_days and (contribution_margin_pct or 0) > 0:
            evidence = [
                item
                for item in (
                    _evidence(state, "inventory", "days_of_supply"),
                    _evidence(state, "economics", "contribution_margin_pct"),
                )
                if item
            ]
            bundle.diagnoses.append(
                Diagnosis(
                    code="CLEARANCE_PACE_TOO_SLOW",
                    summary="Current inventory cover exceeds the time remaining to the clearance deadline.",
                    confidence=Confidence.HIGH,
                    evidence=evidence,
                )
            )
            bundle.actions.append(
                ActionProposal(
                    action_type=ActionType.ADJUST_BID,
                    target={"scope": "high_conversion_targets"},
                    parameters={"relative_change_pct": 10},
                    rationale="The clearance goal favors faster sell-through while contribution margin remains positive.",
                    evidence=evidence,
                    confidence=Confidence.MEDIUM,
                    risk=RiskLevel.MEDIUM,
                    verification_plan={"window_hours": 72, "metrics": ["units_7d", "days_of_supply", "contribution_margin_pct"]},
                )
            )
        return bundle

    def _market_context_rules(self, state: SellerState, bundle: RecommendationBundle) -> RecommendationBundle:
        competitor_price = _number(state.market, "competitor_price_median")
        own_price = _number(state.pricing, "price")
        sales_change = _number(state.sales, "units_change_pct_7d")
        if competitor_price is None or own_price is None or sales_change is None:
            return bundle

        price_premium = (own_price / competitor_price - 1) if competitor_price > 0 else 0
        if price_premium >= 0.1 and sales_change <= -0.15:
            evidence = [
                item
                for item in (
                    _evidence(state, "market", "competitor_price_median", "Third-party market intelligence; validate before price action."),
                    _evidence(state, "pricing", "price"),
                    _evidence(state, "sales", "units_change_pct_7d"),
                )
                if item
            ]
            bundle.diagnoses.append(
                Diagnosis(
                    code="RELATIVE_PRICE_PRESSURE",
                    summary="Own price carries a material premium while first-party unit sales are declining.",
                    confidence=Confidence.MEDIUM,
                    evidence=evidence,
                )
            )
            bundle.actions.append(
                ActionProposal(
                    action_type=ActionType.ADJUST_PRICE,
                    target={"asin": state.identity.asin},
                    parameters={"mode": "simulate_only", "candidate_discount_pct": 5},
                    rationale="Run unit-economics simulation before any price write; competitor pricing is intelligence, not ground truth.",
                    evidence=evidence,
                    confidence=Confidence.MEDIUM,
                    risk=RiskLevel.HIGH,
                    verification_plan={"requires": ["margin_floor_check", "featured_offer_check"]},
                )
            )
        return bundle
