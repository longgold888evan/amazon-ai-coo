from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class DataSource(StrEnum):
    AMAZON_ADS = "amazon_ads"
    AMAZON_SP_API = "amazon_sp_api"
    AMAZON_BRAND_ANALYTICS = "amazon_brand_analytics"
    AMAZON_MARKETING_STREAM = "amazon_marketing_stream"
    SELLERSPRITE = "sellersprite"
    ERP = "erp"
    MANUAL = "manual"
    DERIVED = "derived"


class DataType(StrEnum):
    FIRST_PARTY = "first_party"
    MARKET_INTELLIGENCE = "market_intelligence"
    BUSINESS_TRUTH = "business_truth"
    DERIVED = "derived"


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalType(StrEnum):
    MAXIMIZE_PROFIT = "maximize_profit"
    GROW_REVENUE = "grow_revenue"
    CLEAR_INVENTORY = "clear_inventory"
    LAUNCH = "launch"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ActionType(StrEnum):
    ADJUST_BID = "adjust_bid"
    ADJUST_BUDGET = "adjust_budget"
    PAUSE_CAMPAIGN = "pause_campaign"
    ENABLE_CAMPAIGN = "enable_campaign"
    ADD_NEGATIVE_KEYWORD = "add_negative_keyword"
    CREATE_EXACT_TARGET = "create_exact_target"
    ADJUST_PRICE = "adjust_price"
    UPDATE_LISTING = "update_listing"
    NO_OP = "no_op"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


MetricValue = float | int | str | bool | None


class ObservedMetric(BaseModel):
    value: MetricValue
    source: DataSource
    data_type: DataType
    observed_at: datetime = Field(default_factory=utc_now)
    confidence: Confidence = Confidence.HIGH
    unit: str | None = None
    window: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductIdentity(BaseModel):
    asin: str
    sku: str | None = None
    marketplace_id: str | None = None
    title: str | None = None


class SellerGoal(BaseModel):
    type: GoalType
    target: float | None = None
    deadline: datetime | None = None
    constraints: dict[str, Any] = Field(default_factory=dict)


class SellerState(BaseModel):
    identity: ProductIdentity
    snapshot_at: datetime = Field(default_factory=utc_now)
    sales: dict[str, ObservedMetric] = Field(default_factory=dict)
    ads: dict[str, ObservedMetric] = Field(default_factory=dict)
    inventory: dict[str, ObservedMetric] = Field(default_factory=dict)
    pricing: dict[str, ObservedMetric] = Field(default_factory=dict)
    listing: dict[str, ObservedMetric] = Field(default_factory=dict)
    market: dict[str, ObservedMetric] = Field(default_factory=dict)
    economics: dict[str, ObservedMetric] = Field(default_factory=dict)
    goals: list[SellerGoal] = Field(default_factory=list)


class Evidence(BaseModel):
    field: str
    value: MetricValue
    source: DataSource
    observed_at: datetime
    confidence: Confidence
    note: str | None = None


class Diagnosis(BaseModel):
    code: str
    summary: str
    confidence: Confidence
    evidence: list[Evidence] = Field(default_factory=list)


class ActionProposal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    action_type: ActionType
    target: dict[str, str]
    parameters: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM
    risk: RiskLevel = RiskLevel.MEDIUM
    requires_approval: bool = True
    status: ActionStatus = ActionStatus.PROPOSED
    created_at: datetime = Field(default_factory=utc_now)
    verification_plan: dict[str, Any] = Field(default_factory=dict)


class RecommendationBundle(BaseModel):
    asin: str
    generated_at: datetime = Field(default_factory=utc_now)
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    actions: list[ActionProposal] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    action_id: str
    success: bool
    executed_at: datetime = Field(default_factory=utc_now)
    provider: str
    external_id: str | None = None
    message: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
