"""MCP server exposing the Pāṭala continuity kernel to AI agents.

Complementary to the official OpenAIRE MCP powered by Alien Intelligence:
- Alien/OpenAIRE supplies current research observations.
- Pāṭala records provenance, commits persistent derived objects, checks freshness,
  propagates invalidation, and exposes proof obligations/resolution state.

Install: pip install -e '.[mcp]'
Run:     PATALA_WORKSPACE=.patala-ci python -m patala_research_ci.mcp_server
"""
from __future__ import annotations

import json
import os


def main():
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise SystemExit("MCP extra not installed. Run: pip install -e '.[mcp]'") from exc

    from .mcp_trace import build_trace, MCPTrace
    from .provenance_guard import candidate_bindings_from_trace, verify_binding
    from .lineage import LineageGraph, LineageArtifact, LineageEdge
    from .service import ResearchCI
    from .store import Workspace
    from .trust import PolicyEngine, ActionPolicy
    from .crux import rank_cruxes

    workspace = os.environ.get("PATALA_WORKSPACE", ".patala-ci")
    ci = ResearchCI(Workspace(workspace))
    mcp = FastMCP("Patala Knowledge Continuity")

    @mcp.tool()
    def record_openaire_mcp_call(tool_name: str, arguments_json: str, result_json: str,
                                 openaire_ids_json: str = "[]", client: str = "AI client",
                                 session_label: str = "") -> dict:
        """Record a call already made through the official OpenAIRE/Alien MCP.

        Credential-like keys are redacted before persistence. No Alien token is required.
        """
        arguments = json.loads(arguments_json or "{}")
        result = json.loads(result_json or "null")
        ids = json.loads(openaire_ids_json or "[]")
        if not isinstance(ids, list):
            raise ValueError("openaire_ids_json must decode to a list")
        trace = build_trace(tool_name=tool_name, arguments=arguments, result=result,
                            openaire_ids=[str(x) for x in ids], client=client,
                            session_label=session_label or None, synthetic=False)
        path = ci.ws.save_mcp_trace(trace)
        ci.ws.ledger.append("mcp.trace_imported", trace.trace_id, {
            "trace_digest": trace.digest, "provider": trace.provider, "connector": trace.connector,
            "calls": len(trace.calls), "openaire_ids": trace.openaire_ids, "synthetic": False,
        })
        return {"trace_id": trace.trace_id, "trace_digest": trace.digest, "stored": str(path), "openaire_ids": trace.openaire_ids}

    @mcp.tool()
    def bind_claim_to_trace(trace_id: str, claim_id: str, claim_text: str, openaire_ids_json: str = "[]") -> dict:
        """Create a source-specific evidence binding from a recorded MCP trace.

        This is a proposed dependency until a verifier/human promotes its authority.
        """
        raw = ci.ws.load_mcp_trace(trace_id)
        raw.pop("trace_digest", None)
        trace = MCPTrace.from_dict(raw)
        selected = json.loads(openaire_ids_json or "[]")
        binding = candidate_bindings_from_trace(claim_id, trace, [str(x) for x in selected] or None)
        verdict = verify_binding(claim_id, claim_text, trace, binding)
        ci.ws.save_binding(binding)
        ci.ws.ledger.append("claim.evidence_bound", claim_id, {
            "binding_id": binding.binding_id, "binding_digest": binding.digest,
            "trace_id": trace_id, "verdict": verdict.status,
        })
        return {"binding": binding.to_dict(), "verdict": verdict.to_dict()}

    @mcp.tool()
    def commit_derived_object(graph_id: str, logical_id: str, kind: str, content_json: str,
                              dependencies_json: str = "[]", specification_json: str = "{}") -> dict:
        """Commit a persistent artifact with explicit dependencies.

        dependencies_json is a list of {upstream_id, kind?, trust?, authority?, selector?}.
        Execution identity is deterministic from specification + resolved upstream identities.
        """
        try:
            graph = ci.ws.load_lineage(graph_id)
        except KeyError:
            graph = LineageGraph()
        deps_raw = json.loads(dependencies_json or "[]")
        deps = [LineageEdge(**x) for x in deps_raw]
        art = graph.add(LineageArtifact(logical_id=logical_id, kind=kind,
            content=json.loads(content_json), specification=json.loads(specification_json or "{}"), dependencies=deps))
        ci.ws.save_lineage(graph_id, graph)
        ci.ws.ledger.append("lineage.artifact_committed", logical_id, {
            "graph_id": graph_id, "artifact_id": art.artifact_id,
            "content_digest": art.content_digest, "execution_key": art.execution_key,
            "dependencies": [d.to_dict() for d in deps],
        })
        return art.to_dict()

    @mcp.tool()
    def invalidate_lineage(graph_id: str, changed_ids_json: str) -> dict:
        """Propagate an upstream change through explicit lineage only."""
        graph = ci.ws.load_lineage(graph_id)
        changed = [str(x) for x in json.loads(changed_ids_json)]
        plan = graph.mark_invalidated(changed)
        ci.ws.save_lineage(graph_id, graph)
        ci.ws.ledger.append("lineage.invalidated", graph_id, plan)
        return plan

    @mcp.tool()
    def check_current(graph_id: str, logical_id: str) -> dict:
        """Return causal freshness of a stored object, not merely its age."""
        graph = ci.ws.load_lineage(graph_id)
        node = graph.nodes[logical_id]
        return {"logical_id": logical_id, "state": node.state, "content_digest": node.content_digest,
                "execution_key": node.execution_key, "dependencies": [d.to_dict() for d in node.dependencies]}

    @mcp.tool()
    def evaluate_action(graph_id: str, logical_id: str, action: str, minimum_trust: float = 0.7) -> dict:
        """Risk-sensitive action gate over provenance/trust state."""
        graph = ci.ws.load_lineage(graph_id)
        return PolicyEngine().evaluate(graph, logical_id, ActionPolicy(action, minimum_path_trust=minimum_trust)).to_dict()

    @mcp.tool()
    def find_structural_cruxes(graph_id: str, target_ids_json: str) -> list[dict]:
        """Rank upstream nodes by how much target-relevant downstream state depends on them."""
        graph = ci.ws.load_lineage(graph_id)
        return [x.to_dict() for x in rank_cruxes(graph, [str(v) for v in json.loads(target_ids_json)])]

    @mcp.tool()
    def bind_mcp_trace(analysis_id: str, trace_id: str) -> dict:
        """Bind an OpenAIRE MCP evidence trace to a tracked Research CI analysis."""
        return ci.ws.bind_mcp_trace(analysis_id, trace_id)

    @mcp.tool()
    def verify_analysis(analysis_id: str) -> dict:
        """Recheck an analysis against current OpenAIRE and return minimal downstream impact."""
        r = ci.verify(analysis_id)
        return {"diff": r["diff"].to_dict(), "impact": r["impact"].to_dict(), "obligations": [x.to_dict() for x in r["obligations"]]}

    @mcp.tool()
    def list_proof_obligations() -> list[dict]:
        return ci.ws.list_obligations()

    @mcp.tool()
    def list_tracked_analyses() -> list[dict]:
        return ci.ws.list_analyses()

    @mcp.tool()
    def list_mcp_traces() -> list[dict]:
        return ci.ws.list_mcp_traces()

    @mcp.tool()
    def verify_ledger() -> dict:
        ok, reason = ci.ws.ledger.verify()
        return {"ok": ok, "reason": reason, "state_digest": ci.ws.ledger.state_digest()}

    mcp.run()


if __name__ == "__main__":
    main()
