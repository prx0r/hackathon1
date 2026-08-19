# Pāṭala Research CI

**Continuous verification for AI-native Open Science.**

> **When OpenAIRE changes, know exactly what your research agent needs to recheck.**

OpenAIRE AI Hackathon 2026 — **Theme B: Build**.

## 30-second explanation

The official **OpenAIRE MCP through Alien Intelligence** lets an AI agent query authoritative scholarly metadata. Pāṭala Research CI solves the next lifecycle problem: the agent may retain a conclusion after the OpenAIRE Graph has changed.

Pāṭala records a credential-redacted MCP evidence trace, creates a deterministic OpenAIRE Graph snapshot, attaches explicit dependencies from claims to the Graph observations they use, then later computes:

```text
MCP evidence → snapshot → Graph changes → affected claims → proof obligations → verification receipts
```

It is **not** another literature-search agent, another scholarly graph, or generic graph versioning. It is a continuity layer for conclusions derived from changing research intelligence.

## Why OpenAIRE + Alien MCP + Pāṭala

```text
AI client
   │
   ├── Official OpenAIRE MCP / Alien ── discovery, structured evidence
   │                 │
   │            redacted MCP trace
   │                 │
   └── Pāṭala Research CI
                     │
              OpenAIRE Graph V3
              deterministic snapshot
                     │
                 later refresh
                     │
                 semantic diff
                     │
              explicit dependencies
                     │
          CURRENT / RECHECK REQUIRED
                     │
               ProofObligation
                     │
              ResolutionPlan
                     │
            VerificationReceipt
```

**V3 is the deterministic default** because OpenAIRE documents it as the latest recommended Graph API. V4 is supported as an optional beta adapter. ScholeXplorer V3 adds typed scholarly relations. Broker is modeled as a future event-trigger source.

## Judge-first rubric map

| Criterion | Evidence in this repository |
|---|---|
| **1. OpenAIRE/Alien MCP** | `mcp_trace.py`, `mcp_server.py`, `MCP_AGENT_WORKFLOW.md`, trace import/binding CLI, credential-redaction tests. Bundled trace is explicitly synthetic; capture one real Alien call before final submission. |
| **2. Usefulness/value** | A persistent analysis learns which conclusions actually need attention instead of rerunning everything or silently going stale. |
| **3. Originality** | The contribution begins **after** discovery/versioning: `Graph change → explicit claim impact → frozen proof obligation → evidence receipt`. |
| **4. Responsible data** | `DATA_AND_RIGHTS.md`, OpenAIRE CC-BY attribution, no paywalled full-text redistribution, secret redaction, source-health semantics. |
| **5. Reproducibility/interoperability** | Offline fixtures/tests, schemas, hash-chained ledger, build certificate, RO-Crate export, `CITATION.cff`, CodeMeta/Zenodo metadata. |
| **6. Clarity** | One loop, one deterministic demo, `SUBMISSION_FINAL.md`, ~2-minute `VIDEO_SCRIPT.md`. |

See [`SCORING_MATRIX.md`](SCORING_MATRIX.md) for the adversarial self-review.

## Run the deterministic demo

Core runtime: Python 3.10+, standard library only.

```bash
python -m patala_research_ci.cli --workspace /tmp/patala-demo demo
```

The demo deliberately contains both changes that matter and changes that do not. It proves that unrelated claims remain current, affected claims get targeted obligations, computable claims can be re-evaluated, and the evidence ledger verifies.

Run all tests and the release gate:

```bash
python -m unittest discover -s tests -v
python scripts/verify_release.py
```

## Use with the official OpenAIRE MCP

The hackathon AI connector is **not reimplemented** here. Use the OpenAIRE MCP through Alien for discovery, then preserve its evidence in Pāṭala.

From an AI client that has both the OpenAIRE MCP and Pāṭala's companion MCP available:

1. Query OpenAIRE using the official Alien connector.
2. Call Pāṭala `record_openaire_mcp_call` with the structured tool name/arguments/result.
3. Track the reproducible V3 query and bind the resulting trace.
4. Later call `verify_analysis`.

Or import an exported trace:

```bash
patala-ci --workspace .patala-live mcp-import alien-trace.json --bind analysis:my-review
```

`MCP_AGENT_WORKFLOW.md` gives the full workflow and explains the bundled **synthetic** trace. No claim is made that the synthetic file is evidence of a credentialed Alien session.

## Live OpenAIRE tracking

```bash
pip install -e .
patala-ci --workspace .patala-live track \
  --id agentic-software \
  --title "Agentic AI research software" \
  --entity research-products \
  --search "agentic AI" \
  --api v3 --page-size 25 \
  --claims examples/live_claims.json

# Run later:
patala-ci --workspace .patala-live verify agentic-software
patala-ci --workspace .patala-live verify-ledger
```

A source error is never treated as zero results. A partial relation source never manufactures relation deletion. Failed refreshes do not replace the last known-good snapshot.

## Architecture

Implemented modules include:

- Graph V3 + optional V4 beta + ScholeXplorer + Broker adapters;
- canonical snapshot/digest generation;
- MCP trace capture/redaction/digest/binding;
- entity/field/relation/query-membership dependencies;
- semantic diff/materiality classification;
- claim impact and proof-obligation generation;
- frozen resolution plans and verification receipts;
- append-only hash-chained ledger;
- RO-Crate-compatible export;
- optional companion MCP server and read-only dashboard.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/OPENAIRE_FULL_STACK.md`](docs/OPENAIRE_FULL_STACK.md).

## Critical invariants

```text
SOURCE FAILURE ≠ ZERO RESULTS
PARTIAL SOURCE ≠ COMPLETE RESULT SET
UNKNOWN RELATION ≠ REMOVED RELATION
COSMETIC CHANGE ≠ MATERIAL CHANGE
UPSTREAM CHANGE ≠ CONCLUSION FALSE
NO EXPLICIT DEPENDENCY ≠ IMPACT
AGENT SAYS “FIXED” ≠ PROVEN RESOLUTION
```

## FAIR / reuse

- **Findable:** public Git repository + `CITATION.cff` + CodeMeta/Zenodo metadata.
- **Accessible:** open licenses and a fully offline deterministic demo.
- **Interoperable:** OpenAIRE Graph, official MCP trace boundary, JSON Schemas, RO-Crate-compatible export.
- **Reusable:** small Python package, explicit source contracts, adversarial tests, frozen verification plans.

See [`FAIR.md`](FAIR.md), [`DATA_AND_RIGHTS.md`](DATA_AND_RIGHTS.md), and [`NOTICE.md`](NOTICE.md).

## Submission documents

- **[`SUBMISSION_FINAL.md`](SUBMISSION_FINAL.md)** — exact judge-facing form.
- [`SUBMISSION_STORY.md`](SUBMISSION_STORY.md) — compact narrative.
- [`VIDEO_SCRIPT.md`](VIDEO_SCRIPT.md) — ~2-minute walkthrough.
- [`MCP_AGENT_WORKFLOW.md`](MCP_AGENT_WORKFLOW.md) — official-MCP integration workflow.
- [`SCORING_MATRIX.md`](SCORING_MATRIX.md) — six-criterion self-review.
- [`docs/ALTERNATIVE_BUILDS.md`](docs/ALTERNATIVE_BUILDS.md) — five builds considered.
- [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) — prior art and non-claims.

## License

- Code: **MIT**.
- Original submission documentation/media: **CC BY 4.0**.
- Synthetic fixtures: **CC0 1.0**.
- OpenAIRE-derived metadata: **OpenAIRE Graph CC BY terms; acknowledge OpenAIRE**.

See `LICENSE`, `LICENSES/README.md`, and `NOTICE.md`.
