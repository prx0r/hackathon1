# Pitch 1: The Stronger Framing

*2026-08-19 · After reviewing all materials against this strategy*

---

## The shift

**Old framing:** "Skip 58% of recomputation."
**New framing:** "In a world of abundant inference, the scarce resource is knowing what remains justified."

Old framing = compute optimization.
New framing = epistemic continuity for the agentic science era.

---

## The headline

> **OpenAIRE tells an agent what research says now. Pāṭala tells it whether what the agent concluded before still follows.**

Or even better:

> **Alien makes scholarly evidence agent-accessible. Pāṭala makes agent conclusions accountable to that evidence over time.**

---

## The philosophical hook

> **In a world of abundant AI-generated research, the scarce resource is no longer inference. It is knowing what remains justified.**

---

## Why infinite compute makes Pāṭala MORE important, not less

When inference is expensive: worry about generating enough analysis.
When inference becomes abundant: worry about maintaining the validity of everything already generated.

A million agents can search, synthesize, critique, rerun.

They cannot:
- Retroactively recover an evidence dependency never recorded
- Explain why an old recommendation changed
- Distinguish source failure from evidence disappearing
- Decide that a scholarly disagreement has become settled because another model generated another answer

**Compute cannot recreate lost provenance.**

---

## The key distinction

```
WHAT DID THIS CLAIM DEPEND ON?
            ↓
HAS THAT EVIDENCE CHANGED?
            ↓
WHAT DOWNSTREAM OBJECTS INHERIT THE CHANGE?
            ↓
IS THE CLAIM ACTUALLY INVALID,
OR MERELY IN NEED OF REVIEW?
            ↓
WHAT EXACT EVIDENCE WOULD RESOLVE IT?
            ↓
WHO/WHAT IS AUTHORITIVE ENOUGH
TO CLOSE THE OBLIGATION?
```

A million agents cannot reconstruct that history afterward if nobody recorded it.

---

## The Alien positioning

Don't say: "Alien missed Y, Pāṭala fixes it."

Say:

```
OPENAIRE
trusted scholarly intelligence
        ↓
ALIEN
agent-native access + provenance
        ↓
PĀṬALA
continuity of what agents derive
        ↓
AGENT ECOSYSTEM
self-maintaining scholarly intelligence
```

**Alien enables a new world in which this problem appears.**

---

## The honest admission

There IS a world where Pāṭala is unnecessary:

```
nothing derived is ever persisted
+ every answer is reconstructed from scratch
+ all sources are currently available
+ every computation is exactly reproducible
+ nothing downstream acts on old results
+ no human reports/papers/policies/memories
```

Then just regenerate.

But useful agents accumulate:
memories, hypotheses, reports, plans, recommendations, models, decisions, messages to other agents, actions in the world.

Once an output persists or causes another output, you have **lineage**.
Once lineage exists, changes propagate.

That's why build systems don't disappear because CPUs get faster. Git doesn't disappear because rebuilding is cheap.

**Pāṭala is dependency management / CI for epistemic state.**

---

## What to remove from the pitch

- "Skip 58% of recomputation" → demote to secondary benefit
- "11 are provably current" → say "11 dependencies triggered no recheck" (not "proven true")
- Merkle trees, 33 tests, RO-Crate → evidence underneath, not the hook
- Documentation language at video end → replace with memory hook

## What to promote

- "What remains justified" as the scarce resource
- The three-layer stack: OpenAIRE → Alien → Pāṭala
- The moment: one changed source → one invalidated conclusion → one proof obligation
- The 8-invariants as responsible-use evidence

---

## The video ending

Show:

```
CLAIM C
  depends on relation D → evidence E

OPENAIRE CHANGES:
  relation D removed

RESULT:
  CLAIM C ← REVERIFY_REQUIRED
  Reason: relation D changed
  Action: verify dataset-support dependency

EVERYTHING ELSE:
  CURRENT
```

Then verbally:

> "Alien makes research intelligence available to agents. Pāṭala makes what they learn maintainable. When inference becomes abundant, knowing what remains justified becomes the scarce resource."
