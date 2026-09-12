from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from amazon_ai_coo.domain.models import ActionStatus, RecommendationBundle, SellerState
from amazon_ai_coo.services.action_executor import ActionExecutor
from amazon_ai_coo.services.decision_engine import DecisionEngine
from amazon_ai_coo.services.guardrails import GuardrailEngine
from amazon_ai_coo.services.store import store

router = APIRouter(prefix="/v1")
decision_engine = DecisionEngine()
guardrails = GuardrailEngine()
executor = ActionExecutor()


class ExecuteRequest(BaseModel):
    asin: str


@router.get("/state/{asin}", response_model=SellerState)
def get_state(asin: str) -> SellerState:
    state = store.get_state(asin)
    if state is None:
        raise HTTPException(status_code=404, detail="seller state not found")
    return state


@router.put("/state/{asin}", response_model=SellerState)
def put_state(asin: str, state: SellerState) -> SellerState:
    if state.identity.asin != asin:
        raise HTTPException(status_code=400, detail="path ASIN must match state.identity.asin")
    return store.put_state(state)


@router.post("/recommendations/{asin}", response_model=RecommendationBundle)
def recommendations(asin: str) -> RecommendationBundle:
    state = store.get_state(asin)
    if state is None:
        raise HTTPException(status_code=404, detail="seller state not found")

    bundle = decision_engine.recommend(state)
    for action in bundle.actions:
        store.put_action(action)
    return bundle


@router.post("/actions/{action_id}/approve")
def approve_action(action_id: str):
    action = store.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="action not found")
    if action.status != ActionStatus.PROPOSED:
        raise HTTPException(status_code=409, detail=f"action is already {action.status.value}")
    action.status = ActionStatus.APPROVED
    store.put_action(action)
    return action


@router.post("/actions/{action_id}/execute")
async def execute_action(action_id: str, request: ExecuteRequest):
    action = store.get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="action not found")
    if action.status != ActionStatus.APPROVED:
        raise HTTPException(status_code=409, detail="action must be approved before execution")

    state = store.get_state(request.asin)
    if state is None:
        raise HTTPException(status_code=404, detail="seller state not found")

    guardrail = guardrails.evaluate(action, state)
    if not guardrail.allowed:
        raise HTTPException(status_code=409, detail=f"guardrail blocked action: {guardrail.reason}")

    result = await executor.execute(action)
    if result.success:
        action.status = ActionStatus.EXECUTED
        store.put_action(action)
    return {"action": action, "guardrail": guardrail, "execution": result}
