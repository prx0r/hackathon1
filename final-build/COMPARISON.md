# Final Build Comparison: hackathon1 vs 0.3.0

*2026-08-19 · What the 0.3.0 build adds over hackathon1*

---

## Module count

| | hackathon1 | 0.3.0 (final-build/) |
|--|-----------|----------------------|
| Python modules | ~20 | 48 |
| Tests | 24 | 40 |

## New modules in 0.3.0

| Module | What it does | hackathon1 equivalent | Better? |
|--------|-------------|----------------------|---------|
| `lineage.py` | Generic DAG with 9 artifact kinds, trust edges, cycle detection, topological build, invalidation plan, max_path_trust | `impact.py` (flat dependency walk) | **Much better** — proper DAG, trust propagation, MAP-Graph path trust |
| `merkle.py` | RFC-6962 Merkle with domain separation, inclusion proofs, signed checkpoints | `ledger.py` (simple hash chain) | **Much better** — proper cryptographic integrity |
| `attestation.py` | in-toto Statement v1, Ed25519 signing, signed envelopes | `verification.py` (unsigned receipts) | **Better** — authenticated attestations |
| `provenance_guard.py` | Fail-closed claim/evidence binding, protected literal verification | `compiler.py` (loose ID extraction) | **Much better** — fail-closed, protected literals |
| `mcp_gateway.py` | Hardened Streamable-HTTP client, tool allowlists, schema pinning, legacy fallback | `mcp_trace.py` (trace capture only) | **Much better** — full MCP client |
| `crux.py` | Structural crux ranking by descendant hit rate | None | **New** — dependency-based crux detection |
| `incremental.py` | Incremental recomputation with execution key comparison | None | **New** — selective rebuild |
| `peer_review.py` | Structured review findings with evidence, status machine | None | **New** — evidence-first review |
| `adjudication.py` | Human judgment recording | None | **New** — human authority layer |
| `trust.py` | Path trust computation, action gating | None | **New** — MAP-Graph trust |
| `prov_export.py` | W3C PROV-O export | None | **New** — standards interop |
| `openlineage_export.py` | OpenLineage export | None | **New** — standards interop |

## Key architectural improvements

### 1. Lineage DAG (lineage.py)

hackathon1:
```python
class TrackedClaim:
    dependencies: list[Dependency]  # flat list
```

0.3.0:
```python
class LineageArtifact:
    kind: str  # observation|claim|calculation|section|report|recommendation|memory|review_finding|adjudication
    dependencies: list[LineageEdge]  # with trust, authority, selector
    content_digest: str
    execution_key: str  # different from content_digest!

class LineageGraph:
    # DAG with cycle detection, topological build
    # descendants(), invalidation_plan(), max_path_trust()
```

The `execution_key` distinction is critical: content can be unchanged but the derivation may be unsafe to reuse. That's the correct incremental-computation ground truth.

### 2. Merkle integrity (merkle.py)

hackathon1: simple hash chain
0.3.0: RFC-6962 with domain separation (`\x00` for leaves, `\x01` for nodes), inclusion proofs, signed checkpoints

### 3. ProvenanceGuard (provenance_guard.py)

hackathon1: loose ID extraction from trace
0.3.0: fail-closed verification — DOIs/IDs/numbers in claims MUST appear in selected evidence. Missing = BLOCKED.

### 4. MCP Gateway (mcp_gateway.py)

hackathon1: trace capture only
0.3.0: full Streamable-HTTP client with tool allowlists, schema digest pinning, legacy fallback, credential redaction, source-preserving traces

## What to adopt

For hackathon1 submission, I would adopt:

1. **`lineage.py`** — the DAG model is strictly better than flat dependencies
2. **`merkle.py`** — RFC-6962 is strictly better than simple hash chain
3. **`attestation.py`** — signed statements are strictly better than unsigned receipts
4. **`provenance_guard.py`** — fail-closed is strictly better than loose extraction
5. **`crux.py`** — structural crux is a good addition
6. **`mcp_gateway.py`** — hardened client is strictly better

## What NOT to adopt yet

- `peer_review.py` — scope creep for hackathon1
- `adjudication.py` — scope creep
- `trust.py` — scope creep
- `prov_export.py` — nice but not core
- `openlineage_export.py` — nice but not core

## Recommendation

Copy the 6 core modules into hackathon1's `patala_research_ci/` and update the CLI/service to use the new lineage model. This gives us the strongest possible submission without scope creep.
