# Pāṭala Research CI

**Continuous verification for research built on evolving scholarly knowledge graphs.**

> When the evidence changes, know what to recheck.

---

## What it does

OpenAIRE's Graph contains 386M+ research products that change continuously — records are added, corrected, deduplicated, and sometimes removed. Researchers and AI agents derive conclusions from this data, but when the underlying evidence changes, those conclusions may silently become stale.

Pāṭala Research CI tracks which OpenAIRE records support which research conclusions, detects material changes, and emits proof obligations identifying exactly which conclusions need re-verification.

## Quick start

```bash
# Track an analysis against OpenAIRE
python3 -m patala_research_ci.cli track \
  --name my-analysis \
  --title "Open software in AI research" \
  --search "agentic AI" \
  --entity research-products

# Add a claim with dependencies
python3 -m patala_research_ci.cli claim add \
  --analysis my-analysis \
  --text "Most sampled outputs expose reusable software" \
  --depends "entity:openaire:doi:10.1234/example"

# Verify against current state
python3 -m patala_research_ci.cli verify my-analysis
```

## Architecture

```
OpenAIRE V3 API
    ↓
TrackedAnalysis (query + snapshot + digest)
    ↓
TrackedClaim (conclusion + dependencies)
    ↓
SemanticDiff (materiality-classified changes)
    ↓
ImpactReport (which claims are affected)
    ↓
ProofObligation (frozen acceptance criteria)
    ↓
ResolutionPlan → EvidenceReceipt → RESOLVED
```

## How it works

1. **Track**: Register an OpenAIRE query. Fetch results, canonicalize records, compute content digest.

2. **Claim**: Attach conclusions with explicit dependencies on specific records or relations.

3. **Verify**: Fetch current OpenAIRE state. Compute semantic diff. Match changes against claim dependencies.

4. **Impact**: Classify each claim as CURRENT, SOURCE_CHANGED, RECOMPUTE, or HUMAN_REVIEW.

5. **Oblige**: Emit proof obligations with frozen acceptance criteria that cannot be weakened after creation.

6. **Resolve**: Execute resolution plan, produce evidence receipt, return claim to CURRENT.

## Anti-cheat invariants

```
SOURCE FAILURE ≠ ZERO RESULTS
MISSING FIELD ≠ FALSE
UNKNOWN RELATION ≠ REMOVED RELATION
COSMETIC CHANGE ≠ MATERIAL CHANGE
METADATA UPDATE ≠ CLAIM INVALIDATION
```

## Materiality taxonomy

Not all changes matter equally:

| Class | Example | Triggers obligation? |
|-------|---------|---------------------|
| COSMETIC | Whitespace, formatting | No |
| IDENTITY | ORCID added | No |
| METADATA | Title corrected | Only if claimed |
| RELATION | Dataset link removed | Yes |
| AVAILABILITY | Open access status changed | Only if claimed |
| RETRACTION | Paper retracted | Yes (human review) |

## Reusable components

| Component | What it is | Lines |
|-----------|-----------|-------|
| `openaire.py` | V3 adapter with anti-cheat invariants | ~150 |
| `tracked.py` | TrackedAnalysis + TrackedClaim | ~120 |
| `diff.py` | Semantic diff + materiality | ~130 |
| `impact.py` | Dependency walker | ~100 |
| `obligations.py` | Frozen acceptance criteria | ~130 |
| `ledger.py` | Append-only event store | ~80 |
| `cli.py` | Full CLI | ~200 |
| `verification/` | Plans, receipts, attack catalog | ~300 |
| **Total** | | **~1210** |

## Dependencies

```
httpx>=0.27
```

That's it. One dependency.

## Running from source

```bash
git clone https://github.com/prx0r/hackathon1.git
cd hackathon1
pip install httpx

# Track
python3 -m patala_research_ci.cli track --name test --search "open access"

# Claim
python3 -m patala_research_ci.cli claim add --analysis test --text "OA is growing"

# Verify
python3 -m patala_research_ci.cli verify test

# Log
python3 -m patala_research_ci.cli log

# List
python3 -m patala_research_ci.cli list
```

## License

- Code: MIT
- Documentation: CC-BY 4.0
