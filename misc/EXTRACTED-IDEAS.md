# Ideas Extracted from Patala Vision Docs

*From: newbuild1, patalapath, patalapath2, ideastrends, visionproofdev, commentarialgraph, patalaproducts, scholarlayer, scholarlayer2, scholarproof*

---

## 1. The Identity Distinction (newbuild1)

**Four different things we've been conflating:**

```
IDENTITY    — "What thing are we talking about?"
CONTENT     — "What exact bytes/state did we observe?"
INTERPRETATION — "What do we currently believe?"
REPRESENTATION — "How are we exposing that belief today?"
```

These must be separable. Never encode title, source, hash, date, or version inside an entity ID. Those change. Use opaque UUIDv7 with prefixes:

```
PTW_...  (Work)
PTP_...  (Passage)
PTOBS_... (Observation)
PTEVT_... (Event)
```

**Hackathon relevance:** Our current `entity_id` in OpenAIRE records uses the OpenAIRE internal ID. Should use a stable Pāṭala ID that survives OpenAIRE re-deduplication.

---

## 2. Staleness as a First-Class Concept (patalapath2)

**Steal from ER:** Track staleness per dimension:

```json
{
  "dimension": "translation.eng",
  "state": "SEARCHED_NONE_KNOWN",
  "checked_at": "...",
  "search_protocol": "translation-search/4",
  "freshness": "STALE"
}
```

**Key insight:** A claim of absence should expire. If we searched for dataset links and found none 3 months ago, that absence is stale — new links may have appeared.

**Hackathon relevance:** Our `ClaimState` has CURRENT/STALE/etc. but no temporal expiry on "absence" claims.

---

## 3. ProviderHealth Model (patalapath2)

```json
{
  "provider_id": "openaire",
  "last_discovery_success": "...",
  "freshness": "HEALTHY|DEGRADED|STALE|BLOCKED|RETIRED",
  "records_seen": 175,
  "duplicate_rate": 0.03,
  "metadata_yield": 0.95,
  "rights_clarity": 0.8
}
```

**Hackathon relevance:** Our `SourceStatus` is just OK/PARTIAL/UNAVAILABLE. This is much richer.

---

## 4. Observed vs Inferred vs Estimated (patalapath2)

```
OBSERVED    — directly seen in source
INFERRED    — derived by algorithm
ESTIMATED   — computed from partial data
ASSERTED    — claimed without evidence
ADJUDICATED — verified by human expert
```

**Never collapse them.** This maps directly to our `EpistemicLevel` but adds ESTIMATED and ASSERTED.

**Hackathon relevance:** Our epistemic ladder has 4 levels. This adds 2 more that are useful.

---

## 5. Agent Trajectory (ideastrends)

```
2024: AI → answers
2025: AI → tool calls
2026: AI → long-running work, browser control, other agents, payments, MCP, humans
2027: AI → budgets, persistent authority, procurement, physical-world delegation
```

The scarce resources shift from intelligence to:

```
AUTHORITY  — What may the agent do?
MONEY      — What can it spend?
IDENTITY   — Who is acting?
TRUST      — Who should it interact with?
REALITY    — What is actually happening?
EXECUTION  — Who/what can physically accomplish something?
VERIFICATION — Did it really happen?
LIABILITY  — Who is responsible?
ATTENTION  — When must a human intervene?
```

**Hackathon relevance:** Our product sits at VERIFICATION + ATTENTION. That's the right niche.

---

## 6. Commentary Layer (commentarialgraph)

Transform papers into computable scholarly objects:

```yaml
ScholarlyWork:
  questions answered
  claims made
  interpretations proposed
  primary passages interpreted
  evidence used
  arguments
  distinctions
  definitions / term senses
  objections to other scholars
  agreements / disagreements
  comparisons
  quotations
  uncertainty / qualifications
  citations and their roles
  open questions
```

**Key distinction:** `PRIMARY SOURCE SAYS X` ≠ `RATIÉ INTERPRETS SOURCE AS X` ≠ `RATIÉ'S INTERPRETATION IS CORRECT`

**Hackathon relevance:** Our dependency model currently tracks entity-level dependencies. This suggests tracking claim-level dependencies with richer semantics.

---

## 7. Proof-Carrying Translation Vertical (visionproofdev)

```text
Passage
├── SOURCE exact witness/span
├── T1 transliteral gloss → T1Proof
├── L0 structured token record → L0Proof
├── ArgumentMap → ArgumentMapProof
├── L2 readable translation → L2FaithfulnessProof
├── L200 translation audit → L200ClassificationProof
└── C1 passage commentary → C1LocalityProof
```

**Key insight:** The output is not merely a translation. It is **a translation whose derivation can be audited backwards to the source and whose uncertainty remains explicit.**

**Hackathon relevance:** This is exactly what ProofObligations + VerificationReceipts do for our system.

---

## 8. ContributionEnvelope (patalapath2)

A universal contract between subsystems:

```yaml
ContributionEnvelope:
  producer: Factory | Eval | Scholar | Collation
  consumer: OpenPatala
  object_type: translation | evaluation | review | ...
  object_id: ...
  content_digest: ...
  evidence: ...
  timestamp: ...
```

**Hackathon relevance:** This is the pattern for how different Pāṭala subsystems emit verified outputs. Maps to our MCP trace → evidence binding flow.

---

## 9. The One Architecture (patalapath2)

```text
WRITE SIDE: SOURCE → T1 → ARGMAP → L0 → L2 → L200 → C1
READ SIDE: projection compiler → immutable bundles → MCP/SEO/Astro
```

**Key insight:** "Compute on write, read from bytes." A new document should NOT rebuild the whole corpus.

**Hackathon relevance:** Our verification is the "write side" — compute the impact on write, expose through reads.

---

## 10. The Strongest Hackathon Idea from These Docs

Combining the freshness model (patalapath2) + the agent trajectory (ideastrends) + the identity distinction (newbuild1):

**Pāṭala as the freshness layer for agent memory in the 2026-2027 agent economy.**

When agents move from "answering questions" to "taking actions" to "spending money" to "coordinating workers," every persistent output needs:

1. Stable identity (UUIDv7, not content hash)
2. Dependency recording (what evidence was used)
3. Freshness tracking (when was this last verified)
4. Staleness propagation (when source changes, what downstream is affected)
5. Proof obligations (what check would restore confidence)
6. Verification receipts (cryptographic proof that the check happened)

That's exactly what we built. And these docs confirm that the Pāṭala team was already heading in this direction.

---

## What to add to hackathon1

The strongest additions from these docs:

1. **Staleness expiry** — absence claims should expire (from patalapath2)
2. **ProviderHealth model** — richer source status (from patalapath2)
3. **Observed/Inferred/Estimated/Asserted/Adjudicated** — 5-level epistemic ladder (from patalapath2)
4. **Stable entity IDs** — UUIDv7 with prefixes, not content hashes (from newbuild1)
5. **The agent trajectory framing** — "scarce resource shifts from intelligence to verification" (from ideastrends)
