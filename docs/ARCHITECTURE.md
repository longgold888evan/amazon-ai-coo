# Amazon AI COO — Target Architecture

## 1. Goal

Build a system that can continuously understand the seller's operating state, compare it with market/competitor context, recommend the next best actions, safely execute approved actions, and verify whether those actions worked.

The system is not an LLM wrapper around Seller Central. It is a seller operating system with a canonical world model and an auditable control loop.

```text
Observe -> Normalize -> Seller World Model -> Diagnose -> Plan -> Simulate
       -> Guardrails -> Approve/Execute -> Verify -> Learn -> Observe ...
```

## 2. Source-of-truth hierarchy

### Tier A — First-party seller truth

Amazon-owned data is authoritative for the seller's own business:

- Amazon Ads API: campaign/ad group/target/search term/placement/budget/bid/performance.
- Selling Partner API: orders, FBA inventory, listings/catalog, pricing, finance/fees and supported reports.
- Brand Analytics / search-performance reports where available.
- Amazon Marketing Stream where useful for lower-latency advertising signals.

Use: state, diagnosis, verification and execution.

### Tier B — Business truth

Internal data the marketplaces do not know:

- COGS
- packaging
- freight / duties
- certification cost
- MOQ
- production and inbound lead times
- supplier capacity
- cash constraints
- target margin / inventory goals

Use: unit economics and policy constraints.

### Tier C — Market intelligence

SellerSprite is the first market-intelligence adapter:

- competitor ASINs and estimated trends
- traffic/search keywords
- market demand/trends
- market/brand/seller concentration
- reviews and consumer-intent intelligence
- external trend proxies exposed through its tool surface

Future optional adapters: Keepa direct, Google Trends direct, social/creative sources, ERP and warehouse systems.

Use: hypotheses, relative positioning and opportunity discovery. Third-party estimates never override first-party truth.

## 3. Canonical Seller World Model

Every metric is normalized into `ObservedMetric`:

```text
value
source
source data type
observed_at
confidence
unit/window
metadata
```

The product-level state is separated into domains:

```text
identity
sales
ads
inventory
pricing
listing
market
economics
goals
```

This avoids coupling business reasoning to any vendor-specific payload.

### Recommended canonical metric keys

Initial keys should remain small and stable.

**Sales**
- `revenue_7d`
- `units_7d`
- `units_change_pct_7d`
- `cvr_7d`

**Ads**
- `spend_7d`
- `sales_7d`
- `acos_7d`
- `roas_7d`
- `ctr_7d`
- `cvr_7d`
- `budget_utilization_7d`

**Inventory**
- `fulfillable_units`
- `inbound_units`
- `reserved_units`
- `days_of_supply`

**Pricing**
- `price`
- `featured_offer_owned`

**Market**
- `competitor_price_median`
- `competitor_sales_growth_pct`
- `search_demand_growth_pct`
- `market_concentration`

**Economics**
- `cogs_per_unit`
- `amazon_fees_per_unit`
- `freight_per_unit`
- `contribution_margin_pct`
- `break_even_acos`

## 4. Runtime components

```text
                    +--------------------------+
                    |      Control/API UI      |
                    +------------+-------------+
                                 |
              +------------------v------------------+
              |        Orchestrator / Scheduler     |
              +---------+-------------------+--------+
                        |                   |
          +-------------v----+       +------v---------------+
          | Ingestion Layer  |       | Action/Verify Layer  |
          +--------+---------+       +-----------+----------+
                   |                             |
   +---------------+----------------+            |
   |               |                |            |
Amazon Ads       SP-API        SellerSprite      |
   |               |                |            |
   +---------------+----------------+            |
                   |                             |
          +--------v---------+                   |
          | Normalization    |                   |
          +--------+---------+                   |
                   |                             |
          +--------v-----------------------------v---+
          |      Unified Seller State + History      |
          +--------+-----------------------------+---+
                   |                             ^
          +--------v---------+                   |
          | Decision Engine  |                   |
          | rules + planner  |                   |
          +--------+---------+                   |
                   |                             |
          +--------v---------+                   |
          | Unit Economics   |                   |
          | / Simulation     |                   |
          +--------+---------+                   |
                   |                             |
          +--------v---------+                   |
          | Guardrail Engine |                   |
          +--------+---------+                   |
                   |                             |
          +--------v---------+                   |
          | Approval Policy  |                   |
          +--------+---------+                   |
                   |                             |
          +--------v---------+                   |
          | Action Executor  +-------------------+
          +------------------+
```

## 5. Decision architecture

Do not let a free-form LLM call write APIs directly.

### Step 1 — Deterministic facts and derived metrics

Compute repeatable values first: unit economics, break-even ACOS, days of supply, deltas, shares and constraints.

### Step 2 — Diagnosis

Produce structured diagnoses with evidence and confidence, for example:

- `ADS_ABOVE_BREAK_EVEN`
- `PROFITABLE_BUDGET_CONSTRAINED`
- `CLEARANCE_PACE_TOO_SLOW`
- `RELATIVE_PRICE_PRESSURE`

### Step 3 — Planner

Rules cover obvious high-confidence cases. An LLM planner can later combine cross-domain signals and create a structured `ActionProposal`, but must use the same schema as deterministic rules.

### Step 4 — Simulation

Before price, budget, inventory or other high-impact actions, estimate expected unit economics and plausible downside.

### Step 5 — Guardrails

Examples:

- maximum bid/budget change per action
- minimum contribution margin
- minimum inventory buffer
- max daily spend increase
- no price change from third-party intelligence alone
- no listing write without explicit approval
- per-ASIN and account-level kill switches

### Step 6 — Approval policy

Initial policy:

- read-only: automatic
- recommendations: automatic
- ad writes: human approval
- price/listing writes: blocked or explicit human approval after simulation

Automation rights can later be earned per action type using measured reliability.

### Step 7 — Verification

Every action carries a verification plan:

```text
baseline snapshot
execution timestamp
expected direction
observation window
success metrics
guardrail / rollback criteria
```

The system should distinguish correlation from confident causality; normal operational writes are not automatically experiments.

## 6. Data cadence

Use source-specific freshness instead of pretending all data is real-time:

- event/stream sources: ingest as delivered and aggregate into short windows
- Ads/report APIs: poll according to report freshness and rate limits
- orders/inventory/pricing: poll more frequently when operationally useful
- SellerSprite/market intelligence: slower cadence; refresh only when the information can materially change a decision
- costs/supplier constraints: event-driven when changed

Each metric's `observed_at` prevents stale competitor intelligence from driving fresh operating decisions.

## 7. Storage target

V0 uses an in-memory repository only to stabilize contracts.

Target persistence:

- PostgreSQL: seller/product/config/action/audit metadata and normalized snapshots
- time-series snapshot tables (initially PostgreSQL partitioning is sufficient)
- object storage: raw vendor payloads and report files for replay/audit
- Redis only if later required for locks, short-lived queues or rate limiting

Do not add a vector database for numeric operating state. Embeddings are useful later for reviews, listing text, support docs and unstructured knowledge—not for core metrics.

## 8. Multi-agent policy

Start as a modular monolith, not a swarm.

Logical agents can emerge behind stable services:

- Ads Analyst
- Search/Keyword Analyst
- Competitor Analyst
- Inventory Planner
- Pricing Analyst
- Listing Analyst
- Profit Controller
- Executive Planner

They all read the same Seller World Model and emit the same diagnosis/action contracts. The Executive Planner resolves conflicts against seller goals and account-level constraints.

## 9. Security and tenancy

- never commit credentials
- encrypt refresh tokens/secrets at rest
- least-privilege scopes
- idempotency keys for writes
- append-only action/audit log
- per-seller tenant isolation before design partners are onboarded
- explicit environment separation for dry-run/sandbox/production

## 10. Build plan

### V0 — now

- canonical seller-state schema
- source/confidence provenance
- FastAPI control surface
- deterministic recommendation engine
- guardrails
- approval flow
- dry-run executor
- tests with realistic sample state

### V1 — first real data

1. Add PostgreSQL migrations and snapshot history.
2. Implement Amazon Ads OAuth/report ingestion read-only.
3. Implement SP-API auth and read-only orders/inventory/pricing/finance ingestion.
4. Implement SellerSprite MCP transport and normalization.
5. Add COGS/supply-chain import.
6. Run Forgewood as a live read-only digital twin.

### V2 — first closed loop

1. Ads bid/budget/pause/negative-keyword actions.
2. Human approval queue.
3. Idempotent executor and action audit log.
4. Baseline vs post-action verification.
5. Daily executive operating brief.

### V3 — cross-domain COO

- keyword harvesting + listing/search feedback loop
- pricing simulation
- inventory/advertising coordination
- contribution-profit optimization
- goal-aware planning (profit / growth / clearance / launch)

### V4 — design partners / SaaS

- tenant isolation
- seller-specific policies/goals
- capability discovery per marketplace/account
- observability/SLOs
- billing/entitlements
- replay/evaluation harness

## 11. Definition of success for Forgewood pilot

The system is useful when it can answer, with evidence:

1. What materially changed since the previous snapshot?
2. Why are revenue/profit/traffic/conversion changing?
3. Is the cause internal, Amazon-marketplace-wide, or competitor-driven?
4. What are the top actions ranked by expected value and risk?
5. Which actions are safe to execute now?
6. Did the previous action actually improve the intended metric without violating constraints?

That closed loop is the product. Individual API connectors are implementation details.
