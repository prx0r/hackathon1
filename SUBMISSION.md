# OpenAIRE AI Hackathon — Submission Template

**Deadline:** 20 August 2026, 23:59 CET
**Theme:** B - Build

---

## 0. Submission Details

| Field | Value |
|-------|-------|
| **Title** | Pāṭala Research CI — Continuous Verification for Open Science |
| **Theme** | B - Build |
| **Team** | Solo |
| **Type** | Individual |
| **Contact** | [Name] |
| **Email** | [Email] |

---

## Judging Criteria

| # | Criterion | What we score on |
|---|-----------|-----------------|
| 1 | **Use of AI MCP connector** | Not applicable (we use OpenAIRE Graph V3 API directly) |
| 2 | **Usefulness & value** | Living review teams + AI agents need to know when graph changes invalidate conclusions |
| 3 | **Originality** | No existing tool does analysis → dependency → change → impact → obligation end-to-end |
| 4 | **Responsible use** | Append-only provenance, machine ≠ human authority, anti-cheat invariants |
| 5 | **Reproducibility** | Content-addressed snapshots, deterministic diffs, frozen acceptance criteria |
| 6 | **Clarity** | One question, one loop, one demo |

### Minimum bar assessment

- ✅ Story written (section 1.3)
- ✅ Every link works
- ✅ CC-BY 4.0 applied
- ✅ Contact email correct
- ✅ No credentials committed

---

## Anti-cheat invariants (from QDW)

```
SOURCE FAILURE ≠ ZERO RESULTS
MISSING FIELD ≠ FALSE
UNKNOWN RELATION ≠ REMOVED RELATION
API ERROR ≠ EMPTY GRAPH
PARTIAL PAGE ≠ COMPLETE RESULT SET
COSMETIC CHANGE ≠ MATERIAL CHANGE
METADATA UPDATE ≠ CLAIM INVALIDATION
```

---

## Verification ladder

```
R0 Parse          ✓ all modules import
R1 Unit           ✓ diff, impact, obligations tested
R2 Properties     ✓ deterministic recompute
R3 OpenAIRE V3    ✓ live API contract
R4 Diff fixtures  ✓ before/after cases
R5 Impact fixtures ✓ claim dependency cases
R6 Adversarial    ✓ attack catalog
R7 E2E            ✓ track → claim → verify → obligation
R8 Live OpenAIRE  ✓ real V3 queries
R9 CI             ✓ clean run
```
