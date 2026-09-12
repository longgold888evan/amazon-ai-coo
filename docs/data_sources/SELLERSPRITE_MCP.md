# SellerSprite MCP — Tool Catalog & Routing Policy

Last verified: 2026-09-12

Official MCP catalog: https://open.sellersprite.com/mcp

## 1. Role in Amazon AI COO

SellerSprite is the **external market-intelligence layer**. It is used for competitor, market, keyword, traffic, review, trend and trademark intelligence.

### Source-of-truth rule

**If Amazon first-party APIs expose the same seller-owned fact, Amazon wins.**

Priority order:

1. **Amazon Ads API / Amazon Marketing Stream / Amazon Ads reports** — authoritative for our own campaign, target, search-term, placement, spend, clicks, CPC, conversions, attributed sales, bids and budgets.
2. **Amazon Selling Partner API (SP-API) / Brand Analytics / seller reports** — authoritative for our own orders, units, revenue, inventory, listing, price, Buy Box / Featured Offer, fees and Amazon-provided seller/search analytics where available.
3. **Internal business data** — authoritative for COGS, freight, duties, MOQ, supplier lead time, certification cost, cash constraints and target margin.
4. **SellerSprite MCP** — external estimates and market intelligence: competitors, external keyword demand, traffic structure, category distributions, review intelligence and trend proxies.

SellerSprite may **supplement, benchmark or explain** first-party data, but must not overwrite conflicting first-party Amazon facts.

Examples:

- Our ASIN sales: use SP-API first; SellerSprite `asin_sales_trend` only as an external estimate / cross-check.
- Our paid search term performance: use Amazon Ads API first; SellerSprite `traffic_keyword` / `keyword_conversion` to add market context.
- Competitor ASIN estimated sales: SellerSprite is appropriate because Amazon does not expose competitor seller truth via our APIs.
- Category concentration / competitor traffic / competitor coupons / external reviews: SellerSprite is the primary source.

## 2. Runtime routing rules

Use the smallest tool set that can answer the question. Prefer `returnFields` whenever supported to reduce token and payload cost.

Routing sequence:

```text
User / Agent question
  -> classify fact as OWN-SELLER vs EXTERNAL-MARKET
  -> if OWN-SELLER and Amazon API has it: call Amazon first
  -> identify missing external context
  -> select the minimum SellerSprite tool(s)
  -> normalize into canonical Seller World Model
  -> keep source + observed_at + confidence
  -> never let third-party estimates silently replace first-party facts
```

For decisions that could cause writes (bid, budget, pause/enable, price, listing, inventory), SellerSprite evidence may support the diagnosis, but execution must be based on first-party state plus guardrails and approval policy.

## 3. Official 45 MCP tools

### A. Product / ASIN intelligence (11)

| MCP code | Chinese name | Best use |
|---|---|---|
| `competitor_lookup` | 查竞品 | Batch lookup of target/competitor ASIN commercial metrics such as estimated units/revenue and product details. |
| `product_research` | 选产品 | Screen products by sales/revenue/growth/price/reviews/BSR and other filters. |
| `product_node` | 查产品类目 | Resolve Amazon category/node IDs, names, hierarchy and product counts. |
| `asin_competitor` | 查询 ASIN 竞品数据 | Given an ASIN, discover ASINs with strong competitive relationships. |
| `asin_detail` | ASIN 详情 | ASIN profile: listing date, BSR, A+, seller/product attributes and other detail-page intelligence. |
| `asin_coupon_trend` | ASIN 优惠趋势 | Historical coupon / promotion trend for an ASIN. |
| `asin_detail_with_coupon_trend` | ASIN 详情及优惠趋势 | Combined ASIN detail + coupon trend. |
| `asin_sales_trend` | ASIN 销量趋势 | Parent/child ASIN estimated units and revenue trends. |
| `asin_prediction` | ASIN 销量预测 | Estimate / predict sales for a specified ASIN. |
| `bsr_prediction` | BSR 销量预测 | Estimate sales from BSR. |
| `keepa_info` | 商品趋势详情 (Keepa) | Long-run listing history such as price, BSR, review count and rating trends. |

Recommended patterns:

- Competitor discovery: `asin_competitor -> competitor_lookup`
- Competitor deep dive: `asin_detail -> asin_sales_trend -> asin_coupon_trend -> keepa_info`
- Product opportunity scan: `product_node -> product_research -> asin_competitor -> review`

### B. Keyword / ABA intelligence (11)

| MCP code | Chinese name | Best use |
|---|---|---|
| `traffic_keyword` | 关键词反查（流量词列表） | ASIN -> keywords that generated search-result exposure; natural/ad exposure and ranking context. |
| `keyword_research` | 关键词选品 | Evaluate keyword markets using search demand, purchase rate and related market metrics. |
| `keyword_research_trends` | 关键词选品-趋势数据 | Historical trend for a keyword. |
| `keyword_miner` | 关键词挖掘 | Expand a seed keyword into derivatives and long-tail terms. |
| `traffic_extend` | 拓展流量词 | Multi-ASIN keyword expansion / traffic-word discovery. |
| `keyword_conversion` | 关键字转化率 | Keyword conversion intelligence such as searches, clicks, purchases, conversion, PPC/CPA/ACOS-style benchmarks where returned. |
| `aba_research_weekly` | ABA 数据选品-按周 | Screen / research keywords from weekly ABA metrics. |
| `aba_research_monthly` | ABA 数据选品-按月 | Screen / research keywords from monthly ABA metrics. |
| `aba_research_trend` | ABA 数据选品-关键词趋势 | Historical ABA keyword search trend. |
| `google_trend` | 谷歌趋势 | External Google search trend for a keyword. |
| `keyword_order` | 出单词反查 | Reverse lookup of an ASIN's top order-generating keywords for listing/ads research. |

Recommended patterns:

- Our paid search terms: **Amazon Ads Search Term / targeting reports first**, then `keyword_conversion` for market benchmark.
- Competitor SEO/PPC intelligence: `traffic_keyword -> keyword_order -> keyword_conversion`.
- Keyword expansion: `keyword_miner` for one seed; `traffic_extend` for a competitor-ASIN set.
- Demand history: `keyword_research_trends + aba_research_trend`; add `google_trend` when external interest matters.

### C. Traffic intelligence (4)

| MCP code | Chinese name | Best use |
|---|---|---|
| `traffic_listing` | 关联流量列表 | Product/variant related-traffic sources. |
| `traffic_keyword_stat` | 流量词统计 | Aggregate keyword-traffic structure for an ASIN. |
| `traffic_listing_stat` | 关联流量统计 | Aggregate related-listing traffic structure for an ASIN. |
| `traffic_source` | 查流量来源（关键词流向） | Query which ASINs/keywords receive exposure from a keyword or ASIN. |

Conceptually maintain two graphs:

```text
Search graph:  Keyword <-> ASIN
Related graph: ASIN <-> ASIN
```

### D. Market / category intelligence (14)

| MCP code | Chinese name | Best use |
|---|---|---|
| `market_research` | 选市场列表 | Base category / niche market research dataset. |
| `market_research_statistics` | 选市场-统计 | Aggregate category statistics. |
| `market_product_concentration` | 选市场-商品集中度 | Product concentration / head-product dominance. |
| `market_brand_concentration` | 选市场-品牌集中度 | Brand concentration. |
| `market_seller_country_distribution` | 选市场-卖家所属地分布 | Seller-country composition. |
| `market_seller_concentration` | 选市场-卖家集中度 | Seller concentration. |
| `market_seller_type_concentration` | 选市场-卖家类型分布 | Seller-type mix such as Amazon/FBA/FBM where available. |
| `market_product_demand_trend` | 选市场-商品需求趋势 | Product/category demand trend. |
| `market_listing_date_distribution` | 选市场-上架时间分布 | Listing-age distribution. |
| `market_listing_trend_distribution` | 选市场-上架趋势分布 | New-listing / listing-entry trend. |
| `market_ratings_count_distribution` | 选市场-评分数分布 | Review/rating-count distribution. |
| `market_rating_distribution` | 选市场-评分值分布 | Rating-value distribution. |
| `market_price_distribution` | 选市场-价格分布 | Price-band distribution. |
| `market_ebc_distribution` | 选市场-A+视频分布 | A+ / video content distribution. |

Recommended category evaluation bundle:

```text
product_node
  -> market_research
  -> market_research_statistics
  -> market_product_concentration
  -> market_brand_concentration
  -> market_seller_concentration
  -> market_product_demand_trend
  -> market_listing_date_distribution
  -> market_price_distribution
  -> market_ratings_count_distribution
```

Call only the extra dimensions required by the decision; do not blindly fan out to all 14 tools.

### E. Reviews (1)

| MCP code | Chinese name | Best use |
|---|---|---|
| `review` | 查评论 | Product review data for pain-point clustering, sentiment, feature gaps and product/listing differentiation. |

Recommended pattern:

`asin_detail -> review -> pain-point clusters -> product/listing/creative hypothesis`

### F. Trademark intelligence (4)

| MCP code | Chinese name | Best use |
|---|---|---|
| `trademark_country_list` | 全球商标库-数据范围 | Discover supported trademark-country datasets. |
| `trademark_detail` | 全球商标库-详情 | Detailed trademark record. |
| `trademark_list` | 全球商标库-列表 | Search/list trademark records. |
| `trademark_stats` | 全球商标库-统计 | Aggregate trademark statistics. |

Use for naming, brand-risk screening and competitor-brand research. It is not a substitute for legal advice or an official trademark-office search when making a final legal decision.

## 4. Task -> tool router

| Intent | First source | SellerSprite tools |
|---|---|---|
| Our campaign / ad group / target performance | Amazon Ads API | Add SellerSprite only for market/competitor benchmark |
| Our search term spend/click/order/CPC/ACOS | Amazon Ads API | `keyword_conversion`, `traffic_keyword` as market context |
| Our orders / true units / revenue | SP-API | `asin_sales_trend` only as external estimate/cross-check |
| Our inventory / Featured Offer / listing state | SP-API | `asin_detail` only for public-market view/context |
| Find competitors for an ASIN | SellerSprite | `asin_competitor`, then `competitor_lookup` |
| Competitor sales / price / coupon trend | SellerSprite | `competitor_lookup`, `asin_sales_trend`, `asin_coupon_trend`, `keepa_info` |
| Competitor traffic keywords | SellerSprite | `traffic_keyword`, `traffic_keyword_stat` |
| Competitor order keywords | SellerSprite | `keyword_order` |
| Keyword market opportunity | SellerSprite | `keyword_research`, `keyword_miner`, `keyword_conversion` |
| Multi-competitor keyword expansion | SellerSprite | `traffic_extend` |
| Category attractiveness | SellerSprite | `product_node`, `market_research`, `market_research_statistics` + selected distribution/concentration tools |
| Product opportunity discovery | SellerSprite | `product_research`, `asin_competitor`, `review`, market tools |
| Customer pain points | SellerSprite | `review` |
| Search-demand trend | SellerSprite / Amazon Brand Analytics if owned data is available | `keyword_research_trends`, `aba_research_trend`, `google_trend` |
| Related-product / browse traffic | SellerSprite | `traffic_listing`, `traffic_listing_stat`, `traffic_source` |
| Brand-name trademark screening | SellerSprite | `trademark_country_list`, `trademark_list`, `trademark_detail`, `trademark_stats` |

## 5. Data-quality contract

Every SellerSprite-derived observation stored in the world model should include at least:

```text
source = sellersprite
source_type = third_party_estimate | third_party_observation | external_trend
observed_at
marketplace
asin / keyword / nodeIdPath (where applicable)
window / month (where applicable)
confidence
raw_tool_code
```

Conflict rule:

```text
Amazon first-party value != SellerSprite estimate
=> retain both observations
=> first-party value is canonical for our own business
=> SellerSprite value remains a benchmark / discrepancy signal
=> never average them into a fake "truth"
```

## 6. Supported marketplaces

Official MCP catalog currently lists:

`US`, `JP`, `UK`, `DE`, `FR`, `IT`, `ES`, `CA`, `IN`, `MX`.

## 7. Maintenance

The machine-readable catalog lives at:

`src/amazon_ai_coo/connectors/sellersprite_registry.json`

When SellerSprite changes its MCP surface:

1. Re-check the official MCP catalog.
2. Update the registry's `verified_at` and tool list.
3. Update routing only if semantics changed.
4. Do not change Amazon-first source priority unless the architecture decision itself changes.
