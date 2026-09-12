# Amazon AI COO

Amazon AI COO is a seller operating system that unifies first-party Amazon operating data, external market intelligence, and business economics into a single state model, then turns that state into explainable recommendations and guarded execution.

## Product loop

```text
Observe -> Normalize -> Build Seller State -> Diagnose -> Plan -> Guardrail -> Approve/Execute -> Verify -> Learn
```

## Data authority

1. **Amazon first-party truth** — Ads API, SP-API, Brand Analytics, Marketing Stream.
2. **Market intelligence** — SellerSprite MCP first; Keepa / Google Trends / other sources later.
3. **Business truth** — COGS, freight, tariffs, lead time, MOQ, cash and supplier data.

Every fact carries `source`, `observed_at`, `confidence`, and `data_type`; estimated competitor data is never treated as equivalent to first-party orders or finance data.

## V0 architecture

- `connectors/` — source-specific adapters; no business decisions live here.
- `domain/` — canonical seller-state and action models.
- `services/state_service.py` — builds the unified seller state.
- `services/decision_engine.py` — deterministic diagnosis/recommendation layer; LLM planning plugs in later.
- `services/guardrails.py` — hard safety/business constraints before any write.
- `services/action_executor.py` — approved action execution abstraction.
- `api/` — FastAPI surface for state, recommendations, approvals and execution.
- `docs/ARCHITECTURE.md` — target architecture and rollout plan.

## Principles

- Amazon APIs are the **ground truth + action layer**.
- SellerSprite is primarily an **observe/intelligence layer**.
- No third-party estimate can directly trigger a destructive write.
- Recommendations must include evidence, confidence, expected effect and rollback/verification criteria.
- Human approval is default for write actions until each action class earns automation rights.
- Every state transition and execution must be auditable.

## Quick start

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn amazon_ai_coo.main:app --reload
```

Then open `http://127.0.0.1:8000/docs`.

## Initial API

- `GET /health`
- `GET /v1/state/{asin}`
- `PUT /v1/state/{asin}`
- `POST /v1/recommendations/{asin}`
- `POST /v1/actions/{action_id}/approve`
- `POST /v1/actions/{action_id}/execute`

V0 deliberately starts with local in-memory persistence and mockable connectors so the decision/state contracts can stabilize before credentials are added. PostgreSQL, scheduling, Amazon auth and SellerSprite MCP transport are the next implementation slice.

## Roadmap

1. Canonical schema + local vertical slice.
2. Amazon Ads read-only ingestion.
3. SP-API read-only ingestion.
4. SellerSprite market-intelligence ingestion.
5. Unified state snapshots + history.
6. Decision engine + evidence + unit-economics simulation.
7. Guarded Ads write path with human approval.
8. Cross-domain pricing/listing/inventory actions.
9. Event-driven verification and learning.
10. Multi-seller SaaS isolation and policy engine.
