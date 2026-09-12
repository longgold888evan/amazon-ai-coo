# Knowledge Architecture

## Goal

Turn heterogeneous Amazon operating knowledge into a versioned decision substrate for Amazon AI COO.

The system separates four layers:

```text
Source Layer
  Amazon official docs / Seller University / Ads Academy
  Brand Analytics / Customer Feedback / seller signals
  Operator playbooks (SCYS / Youlianhui / other verified practitioners)
  External market data (Keepa and future providers)
        ↓
Normalization Layer
  source metadata
  freshness / marketplace / topic tags
  rule extraction
  policy classification
        ↓
Decision Knowledge Layer
  facts
  metrics
  diagnostic rules
  action candidates
  hypotheses / experiments
        ↓
Runtime Governance
  source precedence
  policy guardrails
  seller-state preconditions
  confidence threshold
  approval / execution mode
```

## Source precedence

1. `amazon_policy_current`
2. `amazon_official_current`
3. `amazon_first_party_signal`
4. `verified_operator_recent`
5. `verified_operator_historical`
6. `community_unverified`

Lower-priority knowledge can generate a hypothesis but cannot override a higher-priority policy or platform fact.

## Validity states

- `VALID`: current enough and safe to use.
- `REVIEW_REQUIRED`: potentially useful but must be revalidated against current official docs before execution.
- `STALE`: historically useful, but time-sensitive details are outdated.
- `DEPRECATED`: replaced by a newer official API/process.
- `BLOCKED_BY_POLICY`: must never be turned into an executable action.
- `HYPOTHESIS`: plausible operator insight that requires seller-specific evidence.
- `EXPERIMENTAL`: may be tested only with explicit guardrails and measurement.

## Knowledge item types

- `platform_fact`
- `policy_rule`
- `metric_definition`
- `diagnostic_rule`
- `decision_rule`
- `operator_principle`
- `experiment_template`
- `source_pointer`

## Runtime rule

No operational action should be emitted from operator knowledge alone. The decision engine must combine:

```text
Current Seller State
+ Current Amazon Policy
+ Current Platform Facts
+ Relevant Operator Knowledge
+ Economic Constraints
+ Risk Guardrails
→ Recommendation / Action
```
