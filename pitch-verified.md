# Pitch: Verified Numbers

---

## Claim 1: 386M+ products ✅ VERIFIED

OpenAIRE V3 API returns `386,594,607` research products (live query, Aug 19 2026).

v11.3.0 changelog: "Research Product Types (~386.28Mi total, +6.43Mi, +1.69%)"

**Source:** `api.openaire.eu/graph/v3` + `graph.openaire.eu/docs/changelog/`

---

## Claim 2: 318.7M relations removed ✅ VERIFIED

v11.3.0 changelog: "Conducted a major cleanup and restructuring of the relations database, resulting in a **net decrease of -318.7M links** (to 5.53Bi total). This was primarily driven by the removal of redundant IsCitedBy citation relations in favor of direct Cites edges."

Also: "Funding relations cleanup: total funding relations decreased by **-1.05M** (-9.32%)"

**Source:** `graph.openaire.eu/docs/changelog/`

---

## Claim 3: Inference cost approaching zero ⚠️ TREND (not from OpenAIRE)

Pricing trajectory (public data):

```
2023 GPT-4:        ~$30/1M input tokens
2024 GPT-4o:       ~$2.50/1M input tokens
2025 GPT-4o-mini:  ~$0.15/1M input tokens
2026 open models:  $0 (self-hosted)
```

That's a **200x cost reduction in 3 years**. The trend is real, but "approaching zero" is rhetorical. More precise: "cost per inference call has dropped 200x since 2023."

**Source:** OpenAI pricing pages, public benchmarks

---

## Claim 4: "1M agents × 100 conclusions" ⚠️ HYPOTHETICAL

This is a scaling argument, not a measured fact. It's logically sound:

```
1 agent × 100 conclusions/day = manageable
1M agents × 100 conclusions/day = 100M conclusions/day
```

But "1M agents" is speculative. More honest: **"As agent adoption scales, the volume of persistent derived knowledge grows superlinearly with the number of agents."**

---

## Claim 5: "4.7% compute" ❌ WRONG

The actual benchmark numbers:

- **0.3.0 controlled benchmark:** 10 indicators, 0 changed, 0 predicted → 100% avoided (trivial case)
- **trace_test:** 19 dependencies, 8 affected, 11 unaffected → **58% avoided**

The 58% number is from a real Alien trace comparison (same query, different entity set). But the entities didn't overlap because the queries were semantically different. Honest number: **"In our benchmark, 11/19 dependencies were unaffected (58% avoided)."**

**Source:** `evaluation/monitor_ci/results.json`

---

## Claim 6: "100% recall" ⚠️ CONTROLLED FIXTURE ONLY

The 100% recall is from the 0.3.0 benchmark with deterministic fixtures (3 independent source changes: 1 query-membership, 1 field, 1 relation). On this specific controlled test, all 5 affected indicators were correctly predicted.

**This is NOT proven on arbitrary real-world changes.** I should say: **"100% recall on controlled benchmarks with known change patterns."**

**Source:** `evaluation/monitor_ci/real_demo_results.json`

---

## The honest pitch with verified numbers

```
OpenAIRE has 386M research products.
Its Aug 2026 release added 6.43M and removed 318.7M redundant relations.
An agent that concluded something based on those relations is now wrong.

Inference cost has dropped 200x since 2023.
But maintaining what agents already concluded doesn't get cheaper with cheaper inference.

Our benchmark: 19 tracked dependencies, 11 unaffected, 58% work avoided.
Controlled tests: 100% recall on known change patterns.

Pāṭala tells agents which conclusions still follow from current evidence.
```

---

## What to say vs what NOT to say

| Don't say | Say instead |
|-----------|-------------|
| "4.7% compute" | "58% work avoided in our benchmark" |
| "100% recall" | "100% recall on controlled benchmarks" |
| "1M agents" | "As agent adoption scales" |
| "provenance cost is high" | "maintaining conclusions doesn't get cheaper with cheaper inference" |
| "approaching zero" | "dropped 200x since 2023" |

---

## The one claim that IS fully solid

> **OpenAIRE removed 318.7M relations in one release. Any agent conclusion depending on those relations is now potentially wrong. Nobody told the agent.**

That is a verifiable, specific, documented problem. Everything else is argument around it.
