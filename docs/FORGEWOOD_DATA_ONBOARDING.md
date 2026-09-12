# Forgewood Data Onboarding

## Objective

Make Forgewood the first live digital twin in Amazon AI COO. The system should be able to reconstruct the current operating state, explain changes, compare the business with competitors, recommend actions, and later execute approved actions.

## Safety rule

Never commit secrets to GitHub and never paste Seller Central passwords, MFA codes, API client secrets, refresh tokens, or SellerSprite secret keys into issues/docs/chat. Store secrets only in local `.env` or a production secret manager. The repository contains only variable names and setup instructions.

## Source priority

1. **Amazon first-party truth** — Amazon Ads API, SP-API, Brand Analytics, Marketing Stream.
2. **Forgewood business truth** — COGS, freight, duties, MOQ, lead times, target margins and inventory goals.
3. **Market intelligence** — SellerSprite API; optional direct Keepa/Google Trends/social sources later.
4. **Manual/context data** — operating notes, seasonality, planned promotions, supply constraints.

Third-party estimates can generate hypotheses but must not overwrite Amazon first-party facts.

---

## Batch 1 — needed first

These are enough to create the first live read-only Forgewood digital twin.

### A. Store / product identity (non-secret)

Provide in `config/forgewood.yaml` locally or through a secure admin UI later:

- primary marketplace (`US`, expected for Forgewood)
- marketplace ID
- Seller ID / merchant ID if available
- brand name
- parent ASIN
- every child ASIN
- every seller SKU mapped to ASIN
- product title / color / variation name
- launch date if known
- current business goal per ASIN (for example `CLEAR_INVENTORY`)
- target/deadline for the goal

### B. Unit economics (business truth)

Per SKU/ASIN:

- factory unit cost
- packaging cost
- domestic China logistics per unit
- international freight per unit
- duty/tariff per unit
- Amazon referral fee or fee estimate
- FBA fulfillment fee or fee estimate
- storage cost estimate
- prep/label cost
- expected return/refund loss rate
- other variable costs
- optional fixed costs allocated per unit

Supply-chain constraints:

- MOQ
- supplier lead time
- production lead time
- freight/inbound lead time
- supplier capacity constraints
- reorder policy if any

The system will derive contribution margin, break-even ACOS and sell-through constraints from these values.

### C. Amazon Ads API credentials (secret; local `.env` only)

Required variables:

- `AMAZON_ADS_CLIENT_ID`
- `AMAZON_ADS_CLIENT_SECRET`
- `AMAZON_ADS_REFRESH_TOKEN`
- `AMAZON_ADS_PROFILE_ID`

Amazon Ads API access requires application approval. For the Forgewood pilot, use direct-advertiser access for the account rather than a third-party SaaS authorization model.

First read-only datasets:

- profiles
- campaigns
- ad groups
- product ads
- keywords / product targets
- negative targets
- campaign budgets
- targeting report
- search-term report
- advertised-product report
- placement report
- daily/hourly performance where available

### D. SP-API credentials (secret; local `.env` only)

Required variables:

- `SP_API_CLIENT_ID` (LWA client ID)
- `SP_API_CLIENT_SECRET` (LWA client secret)
- `SP_API_REFRESH_TOKEN`
- `SP_API_MARKETPLACE_ID`
- `SP_API_SELLER_ID` (metadata / validation; not an auth secret)
- `SP_API_REGION` (`na` for the US marketplace)

For a private seller application, self-authorization generates the LWA refresh token. Start with non-restricted roles; we do **not** need customer PII for the COO use case.

First read-only datasets:

- marketplace participation
- orders aggregated at business level (no buyer PII)
- FBA inventory
- listings/catalog metadata
- pricing / featured-offer signals
- fees / finance reports where authorized
- returns/refund aggregates where available
- sales/traffic reports
- Brand Analytics / Search Query Performance where account eligibility allows it
- Customer Feedback data where available

### E. SellerSprite production API (secret; local `.env` only)

For backend/system integration use SellerSprite API rather than depending on MCP transport.

Required variables:

- `SELLERSPRITE_BASE_URL=https://api.sellersprite.com`
- `SELLERSPRITE_API_KEY=<secret key>`

First market-intelligence datasets:

- competitor ASIN discovery
- ASIN competitor set
- estimated sales/rank trends
- price/coupon history where available
- traffic keywords
- keyword demand / conversion intelligence
- ABA research
- market/category research
- review intelligence
- market/brand/seller concentration
- external trend proxies exposed by SellerSprite

Recommended competitor seed: 5–20 ASINs that are genuinely substitutable with Forgewood; the system can expand this set later.

---

## Batch 2 — historical backfill

After live connectivity works, backfill history so diagnoses are not based on only a few days.

Target: at least 12 months when source availability permits; 24 months is preferable for seasonality.

Ingest/backfill:

- daily sales and units
- sessions/page views and conversion
- ad spend, attributed sales, clicks, impressions, CPC, CTR, CVR, ACOS/ROAS
- search terms and targeting performance
- price and coupon/promotion periods
- inventory levels / stockouts / inbound events
- returns/refunds
- Amazon fees and settlements
- listing changes
- rating/review-count history
- competitor price/rank/sales estimates
- major external events / holidays / Prime events

If API onboarding is delayed, temporary CSV exports from Seller Central / Amazon Ads can bootstrap this history. Raw exports should be stored outside git and imported into the system.

---

## Batch 3 — complete operating context

These fields make the COO materially better at decisions that involve cash and supply chain:

- purchase orders
- supplier quotations and cost changes
- available cash / cash budget allocated to inventory
- inbound shipment ETAs
- storage constraints
- planned promotions / Prime events
- liquidation deadline
- target minimum contribution margin
- target TACOS / profit target
- preferred risk tolerance
- actions that require explicit approval
- actions that can eventually be automated

---

## Canonical Forgewood model

Each ASIN/SKU ultimately receives a state like:

```yaml
identity:
  brand: Forgewood Games
  asin: B0...
  sku: ...
  marketplace: US

goal:
  type: CLEAR_INVENTORY
  deadline: 2026-12-31

sales:
  revenue_7d: ...
  units_7d: ...
  sessions_7d: ...
  cvr_7d: ...

ads:
  spend_7d: ...
  sales_7d: ...
  acos_7d: ...
  tacos_7d: ...
  cpc_7d: ...
  ctr_7d: ...
  cvr_7d: ...

inventory:
  fulfillable_units: ...
  inbound_units: ...
  reserved_units: ...
  days_of_supply: ...

pricing:
  price: ...
  featured_offer_owned: ...

market:
  competitor_price_median: ...
  competitor_sales_growth_pct: ...
  search_demand_growth_pct: ...
  market_concentration: ...

unit_economics:
  cogs_per_unit: ...
  freight_per_unit: ...
  amazon_fees_per_unit: ...
  contribution_margin_per_unit: ...
  contribution_margin_pct: ...
  break_even_acos: ...
```

Every metric stores provenance (`source`, `observed_at`, `confidence`, `window`) so intelligence estimates cannot masquerade as first-party truth.

---

## First milestone

**Forgewood Read-only Digital Twin v1** is complete when the system can automatically answer:

1. What changed materially in sales, conversion, ads, inventory, price and profit?
2. Which changes are internal versus market/competitor driven?
3. Which search terms / targets are creating or destroying contribution profit?
4. Is current inventory pacing consistent with the business goal/deadline?
5. What are the top 3–5 actions by expected value, confidence and risk?
6. What evidence supports every recommendation?

No production write action is required for this milestone.
