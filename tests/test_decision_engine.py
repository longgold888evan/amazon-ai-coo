from datetime import datetime, timedelta, timezone

from amazon_ai_coo.domain.models import (
    ActionType,
    Confidence,
    DataSource,
    DataType,
    GoalType,
    ObservedMetric,
    ProductIdentity,
    SellerGoal,
    SellerState,
)
from amazon_ai_coo.services.decision_engine import DecisionEngine


def metric(value, source=DataSource.AMAZON_ADS, data_type=DataType.FIRST_PARTY):
    return ObservedMetric(
        value=value,
        source=source,
        data_type=data_type,
        confidence=Confidence.HIGH,
    )


def test_above_break_even_acos_recommends_bid_reduction():
    state = SellerState(
        identity=ProductIdentity(asin="B0TEST"),
        ads={"acos_7d": metric(0.45)},
        economics={
            "break_even_acos": metric(0.30, DataSource.DERIVED, DataType.DERIVED),
        },
    )

    result = DecisionEngine().recommend(state)

    assert any(d.code == "ADS_ABOVE_BREAK_EVEN" for d in result.diagnoses)
    action = next(a for a in result.actions if a.action_type == ActionType.ADJUST_BID)
    assert action.parameters["relative_change_pct"] == -10
    assert action.requires_approval is True


def test_profitable_budget_constraint_recommends_budget_increase():
    state = SellerState(
        identity=ProductIdentity(asin="B0TEST"),
        ads={
            "acos_7d": metric(0.20),
            "budget_utilization_7d": metric(0.95),
        },
        economics={
            "break_even_acos": metric(0.40, DataSource.DERIVED, DataType.DERIVED),
        },
    )

    result = DecisionEngine().recommend(state)

    assert any(a.action_type == ActionType.ADJUST_BUDGET for a in result.actions)


def test_clearance_rule_respects_goal_and_positive_margin():
    state = SellerState(
        identity=ProductIdentity(asin="B0TEST"),
        inventory={
            "days_of_supply": metric(120, DataSource.DERIVED, DataType.DERIVED),
        },
        economics={
            "contribution_margin_pct": metric(0.15, DataSource.DERIVED, DataType.DERIVED),
        },
        goals=[
            SellerGoal(
                type=GoalType.CLEAR_INVENTORY,
                deadline=datetime.now(timezone.utc) + timedelta(days=60),
            )
        ],
    )

    result = DecisionEngine().recommend(state)

    assert any(d.code == "CLEARANCE_PACE_TOO_SLOW" for d in result.diagnoses)
