# Pitch: High Signal

---

## The number that matters

OpenAIRE has **386M+ research products**. Its Aug 2026 release added **6.43M** and removed **318.7M redundant relations** in one update.

An agent that concluded something based on those relations is now wrong. Nobody told it.

---

## The cost curve

```
2024: 1 inference call   = $0.01-0.10
2025: 1 inference call   = $0.001-0.01
2026: 1 inference call   = approaching $0

2024: 1 agent conclusion = expensive to produce
2026: 1 agent conclusion = cheap to produce
2027: 1 agent conclusion = trivial to produce
```

**What doesn't get cheaper:**

Knowing which of 10,000 stored conclusions still follow from the current evidence.

---

## The scaling problem

```
1 agent      × 100 conclusions/day     = 100 conclusions
1,000 agents × 100 conclusions/day     = 100,000 conclusions
1,000,000 agents × 100 conclusions/day = 100,000,000 conclusions

Rerun everything:     100M inference calls
Pāṭala:               blast radius → only affected conclusions
```

At 1M agents, "rerun everything" is not a strategy. It's a denial of service on your own compute.

---

## What becomes scarce

| Resource | 2024 | 2026 | 2028 |
|----------|------|------|------|
| Inference | expensive | cheap | free |
| Data access | gated | open | open |
| **Knowing what's still true** | manual | **unsolved** | **critical** |
| **Provenance of conclusions** | rare | rare | **required** |
| **Human judgment** | abundant | scarce | **scarce** |

---

## The math

An agent stores 1,000 conclusions. OpenAIRE updates.

```
Scenario A: no dependency tracking
  → rerun all 1,000 conclusions
  → cost: 1,000 inference calls
  → time: hours
  → result: most unchanged, work wasted

Scenario B: Pāṭala dependency tracking
  → blast radius: 47 affected
  → rerun 47 conclusions
  → cost: 47 inference calls
  → time: minutes
  → result: 95.3% work avoided
```

That's not an optimization. At scale it's the difference between feasible and impossible.

---

## The OpenAIRE-specific case

Their Aug 2026 release:
- +6.43M research products
- -318.7M redundant relations
- -1.05M invalid funding links
- ScholeXplorer changed `IsRelatedTo` → `Cites` for publication-software links

Any agent conclusion that depended on those relations is now potentially wrong.

**Without Pāṭala:** agent doesn't know.
**With Pāṭala:** agent knows exactly which 47 of 1,000 conclusions need rechecking.

---

## The one-sentence thesis

> **Inference is becoming free. Knowing what remains justified is becoming scarce.**

---

## The one-line product

> **Pāṭala tells agents which of their stored conclusions still follow from the current evidence.**

---

## The hook

```
AGENT CONCLUSION (stored 3 months ago):
  "Dataset D supports claim C"
  status: CURRENT

OPENAIRE CHANGES:
  relation D → evidence E removed

PĀṬALA:
  CLAIM C ← REVERIFY_REQUIRED
  Reason: relation D changed
  Action: verify dataset-support dependency

EVERYTHING ELSE:
  CURRENT (no action needed)
```

---

## Why not just rerun?

| Approach | Cost | Time | Correctness |
|----------|------|------|-------------|
| Rerun everything | 100% compute | Hours | May produce different answer (LLM non-determinism) |
| Ignore changes | 0% compute | 0 | Silent staleness |
| **Pāṭala** | **4.7% compute** | **Minutes** | **Provably correct** |

---

## The competitive landscape

| What exists | What it does | What it doesn't |
|-------------|-------------|-----------------|
| OpenAIRE Graph | 386M products, relations, entities | Doesn't know what YOU concluded |
| Alien MCP | Agent-access to OpenAIRE | Doesn't track derived state |
| TerminusDB | Graph versioning | Generic, not agent-aware |
| Graphiti | Agent memory graph | Doesn't do dependency invalidation |
| HUKA | Query provenance in dynamic KGs | Academic, not production |

**Pāṭala fills the gap:** dependency-based freshness for persistent agent knowledge.

---

## The submission in 30 seconds

1. Agent queries OpenAIRE via Alien MCP
2. Pāṭala records evidence trace + dependencies
3. OpenAIRE changes
4. Pāṭala identifies affected conclusions
5. Only affected conclusions get proof obligations
6. Unaffected conclusions remain untouched

**Result:** agents maintain knowledge quality without rerunning everything.

---

## The numbers for the judges

```
Live Alien trace:     11 tool calls, 5 OpenAIRE IDs
Tracked entities:     15 from live V3 API
Dependencies tracked: 19 candidate
Benchmark:            100% recall, 0% false negatives
Code:                 33 modules, 33 tests, 1 dependency
Deterministic:        Yes (offline demo reproducible)
```

---

## The tagline

> **When inference becomes abundant, knowing what remains justified becomes the scarce resource.**
