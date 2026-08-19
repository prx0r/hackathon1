from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .dashboard import serve as serve_dashboard
from .export import export_ro_crate
from .model import Dependency, QuerySpec, Snapshot, TrackedClaim
from .mcp_trace import load_trace, build_trace
from .service import ResearchCI
from .store import Workspace


def _kv(values: list[str] | None) -> dict[str, str]:
    out = {}
    for raw in values or []:
        if "=" not in raw:
            raise SystemExit(f"Expected KEY=VALUE, got: {raw}")
        k, v = raw.split("=", 1)
        out[k] = v
    return out


def _print_json(value: Any):
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def _load_claims(path: str | None) -> list[TrackedClaim]:
    if not path:
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("claims", [])
    return [TrackedClaim.from_dict(x) for x in data]


def _load_snapshot(path: str) -> Snapshot:
    return Snapshot.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="patala-ci", description="Continuous verification for evolving scholarly knowledge")
    p.add_argument("--workspace", default=".patala-ci", help="Workspace directory")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("track", help="Track an OpenAIRE query and its claims")
    t.add_argument("--id", required=True); t.add_argument("--title")
    t.add_argument("--entity", default="research-products", choices=["research-products","organizations","datasources","projects","persons"])
    t.add_argument("--search"); t.add_argument("--param", action="append", default=[])
    t.add_argument("--api", default="v3", choices=["v3","v4"])
    t.add_argument("--page-size", type=int, default=25); t.add_argument("--max-pages", type=int, default=1)
    t.add_argument("--relations", action="store_true", help="Enrich research products via ScholeXplorer V3")
    t.add_argument("--relation", help="Optional ScholeXplorer relation semantic")
    t.add_argument("--select", action="append", default=[], help="V4 beta sparse field selection")
    t.add_argument("--facet", action="append", default=[], help="V4 beta facet")
    t.add_argument("--claims", help="JSON file containing TrackedClaim objects")
    t.add_argument("--mcp-trace", help="Alien/OpenAIRE MCP trace JSON to bind to this analysis")

    v = sub.add_parser("verify", help="Re-run a tracked analysis against current OpenAIRE")
    v.add_argument("analysis_id")

    rr = sub.add_parser("resolve", help="Resolve a computable proof obligation with a frozen verification plan")
    rr.add_argument("obligation_id")

    l = sub.add_parser("log", help="Show append-only event history")
    l.add_argument("--tail", type=int, default=50)

    vl = sub.add_parser("verify-ledger", help="Verify hash-chain integrity")

    li = sub.add_parser("list", help="List analyses and proof obligations")

    ex = sub.add_parser("export", help="Export an analysis as an RO-Crate-style ZIP")
    ex.add_argument("analysis_id"); ex.add_argument("--out", required=True)

    d = sub.add_parser("demo", help="Run the complete deterministic offline demo")
    d.add_argument("--fixtures", default=str(Path(__file__).resolve().parents[1] / "fixtures" / "demo"))

    mi = sub.add_parser("mcp-import", help="Import and hash an Alien/OpenAIRE MCP tool-call trace")
    mi.add_argument("trace_file")
    mi.add_argument("--bind", dest="bind_analysis", help="Optional analysis ID to bind the trace to")

    ml = sub.add_parser("mcp-list", help="List imported MCP evidence traces")

    mt = sub.add_parser("mcp-tools", help="List tools from a remote MCP server through the hardened gateway")
    mt.add_argument("--url", default="https://openaire.mcp.alien.club/mcp")
    mt.add_argument("--allow", action="append", default=[]); mt.add_argument("--timeout", type=float, default=45.0)

    mc = sub.add_parser("mcp-call", help="Call one Alien/OpenAIRE MCP tool and persist a provenance trace")
    mc.add_argument("tool"); mc.add_argument("--args-json", default="{}")
    mc.add_argument("--url", default="https://openaire.mcp.alien.club/mcp"); mc.add_argument("--timeout", type=float, default=45.0)
    mc.add_argument("--label"); mc.add_argument("--out-trace")

    tb = sub.add_parser("trace-bind", help="Create and verify an explicit claim-to-MCP-evidence binding")
    tb.add_argument("trace_file"); tb.add_argument("--claim-id", required=True); tb.add_argument("--claim-text", required=True)
    tb.add_argument("--select-id", action="append", default=[])

    ld = sub.add_parser("lineage-demo", help="Build a derived-object DAG from an MCP trace and demonstrate selective invalidation")
    ld.add_argument("trace_file"); ld.add_argument("--graph-id", default="lineage:demo")

    cp = sub.add_parser("checkpoint", help="Create an RFC6962-style Merkle checkpoint over the event ledger")
    cp.add_argument("--id"); cp.add_argument("--private-key"); cp.add_argument("--key-id", default="local-ed25519")

    kg = sub.add_parser("keygen", help="Generate a local Ed25519 keypair for attestations/checkpoints")
    kg.add_argument("--private", required=True); kg.add_argument("--public", required=True)

    at = sub.add_parser("attest", help="Create an in-toto-shaped signed attestation")
    at.add_argument("--subject-name", required=True); at.add_argument("--subject-digest", required=True)
    at.add_argument("--predicate-type", required=True); at.add_argument("--predicate-json", required=True)
    at.add_argument("--private-key", required=True); at.add_argument("--key-id", default="local-ed25519"); at.add_argument("--id")

    le = sub.add_parser("lineage-export", help="Export a stored lineage graph as OpenLineage-shaped JSON or PROV JSON-LD")
    le.add_argument("graph_id"); le.add_argument("--format", choices=["openlineage","prov"], default="prov"); le.add_argument("--out", required=True)

    s = sub.add_parser("serve", help="Serve local read-only dashboard")
    s.add_argument("--host", default="127.0.0.1"); s.add_argument("--port", type=int, default=8765)
    return p


def cmd_track(args, ci: ResearchCI):
    spec = QuerySpec(
        entity=args.entity, search=args.search, filters=_kv(args.param), api_version=args.api,
        page_size=args.page_size, max_pages=args.max_pages, include_scholexplorer=args.relations,
        scholexplorer_relation=args.relation, select=args.select, facets=args.facet,
    )
    analysis = ci.track(args.id, args.title or args.id, spec, claims=_load_claims(args.claims))
    trace_info = None
    if args.mcp_trace:
        trace = load_trace(args.mcp_trace)
        ci.ws.save_mcp_trace(trace)
        ci.ws.ledger.append("mcp.trace_imported", trace.trace_id, {
            "trace_digest": trace.digest, "provider": trace.provider, "connector": trace.connector,
            "synthetic": trace.synthetic, "calls": len(trace.calls), "openaire_ids": trace.openaire_ids,
        })
        ci.ws.bind_mcp_trace(analysis.analysis_id, trace.trace_id)
        trace_info = {"trace_id": trace.trace_id, "digest": trace.digest, "synthetic": trace.synthetic}
    snap = ci.ws.load_snapshot(analysis.latest_snapshot_id)
    _print_json({"analysis": analysis.to_dict(), "snapshot": {"id": snap.snapshot_id, "digest": snap.digest,
                 "source_status": snap.source_status, "items": len(snap.items), "relations": len(snap.relations)},
                 "mcp_trace": trace_info})


def cmd_verify(args, ci: ResearchCI):
    r = ci.verify(args.analysis_id)
    _print_json({
        "diff": r["diff"].to_dict(), "impact": r["impact"].to_dict(),
        "obligations": [x.to_dict() for x in r["obligations"]],
        "ledger_state": ci.ws.ledger.state_digest(),
    })


def cmd_demo(args, ci: ResearchCI):
    fixture = Path(args.fixtures)
    baseline = _load_snapshot(str(fixture / "baseline_snapshot.json"))
    current = _load_snapshot(str(fixture / "current_snapshot.json"))
    claims = _load_claims(str(fixture / "claims.json"))
    spec = QuerySpec.from_dict(baseline.query)
    analysis_id = "demo:software-evidence"
    # Clean collision only inside the chosen demo workspace.
    for folder in ("analyses","snapshots","claims","diffs","impacts","obligations","plans","receipts"):
        for p in (ci.ws.root / folder).glob("*.json"):
            p.unlink()
    ci.ws.ledger.path.write_text("", encoding="utf-8")
    ci.track_from_snapshot(analysis_id, "Open research software and linked datasets", spec, baseline, claims,
                           "Deterministic OpenAIRE-shaped fixture demonstrating impact-aware verification.")
    # Exercise the required OpenAIRE-MCP evidence boundary without pretending that
    # an offline test fixture is a live Alien session. This trace is explicitly synthetic.
    trace = build_trace(
        tool_name="search_research_products",
        arguments={"search": "research software", "page_size": 4},
        result={"source": "OpenAIRE MCP fixture", "items": [{"id": x.get("id")} for x in baseline.items]},
        openaire_ids=[str(x.get("id")) for x in baseline.items if x.get("id")],
        client="Pāṭala deterministic demo",
        session_label="offline synthetic MCP-path test",
        synthetic=True,
    )
    ci.ws.save_mcp_trace(trace)
    ci.ws.ledger.append("mcp.trace_imported", trace.trace_id, {
        "trace_digest": trace.digest, "provider": trace.provider, "connector": trace.connector,
        "synthetic": True, "calls": len(trace.calls), "openaire_ids": trace.openaire_ids,
    })
    ci.ws.bind_mcp_trace(analysis_id, trace.trace_id)
    result = ci.verify(analysis_id, supplied_snapshot=current)
    resolved = []
    for ob in result["obligations"]:
        claim = ci.ws.load_claim(ob.claim_id)
        if claim.computation:
            x = ci.resolve_computable(ob.obligation_id)
            resolved.append({"obligation_id": ob.obligation_id, "claim": claim.claim_id,
                             "result": x["evaluation"], "receipt": x["receipt"].receipt_id,
                             "receipt_valid": x["valid"]})
    ok, reason = ci.ws.ledger.verify()
    _print_json({
        "analysis": analysis_id,
        "mcp_trace": {"trace_id": trace.trace_id, "digest": trace.digest, "synthetic": True,
                      "connector": trace.connector, "openaire_ids": trace.openaire_ids},
        "baseline": baseline.digest,
        "current": current.digest,
        "diff_summary": result["diff"].summary,
        "impact": result["impact"].to_dict(),
        "obligations": [x.to_dict() for x in result["obligations"]],
        "auto_resolved": resolved,
        "ledger": {"ok": ok, "reason": reason, "state_digest": ci.ws.ledger.state_digest()},
    })


def cmd_mcp_import(args, ci: ResearchCI):
    trace = load_trace(args.trace_file)
    path = ci.ws.save_mcp_trace(trace)
    ci.ws.ledger.append("mcp.trace_imported", trace.trace_id, {
        "trace_digest": trace.digest,
        "provider": trace.provider,
        "connector": trace.connector,
        "client": trace.client,
        "synthetic": trace.synthetic,
        "calls": len(trace.calls),
        "openaire_ids": trace.openaire_ids,
    })
    binding = None
    if args.bind_analysis:
        binding = ci.ws.bind_mcp_trace(args.bind_analysis, trace.trace_id)
    _print_json({"trace_id": trace.trace_id, "trace_digest": trace.digest, "stored": str(path),
                 "synthetic": trace.synthetic, "openaire_ids": trace.openaire_ids, "binding": binding})



# --- Continuity-kernel commands -------------------------------------------------

def cmd_mcp_tools(args, ci: ResearchCI):
    from .mcp_gateway import TrustedMCPServer, StreamableHTTPClient
    server = TrustedMCPServer(url=args.url, allowed_tools=tuple(args.allow or []))
    client = StreamableHTTPClient(server, timeout=args.timeout)
    tools = client.list_tools()
    _print_json({"server": args.url, "count": len(tools), "tools": tools})


def cmd_mcp_call(args, ci: ResearchCI):
    from .mcp_gateway import TrustedMCPServer, StreamableHTTPClient, ProvenanceGateway
    arguments = json.loads(args.args_json or "{}")
    server = TrustedMCPServer(url=args.url, allowed_tools=(args.tool,))
    gateway = ProvenanceGateway(StreamableHTTPClient(server, timeout=args.timeout), session_label=args.label)
    result = gateway.call(args.tool, arguments)
    trace = gateway.trace()
    ci.ws.save_mcp_trace(trace)
    ci.ws.ledger.append("mcp.trace_imported", trace.trace_id, {
        "trace_digest": trace.digest, "provider": trace.provider, "connector": trace.connector,
        "synthetic": False, "calls": len(trace.calls), "openaire_ids": trace.openaire_ids,
    })
    if args.out_trace:
        Path(args.out_trace).write_text(json.dumps(trace.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    _print_json({"result": result, "trace_id": trace.trace_id, "trace_digest": trace.digest,
                 "openaire_ids": trace.openaire_ids, "stored": args.out_trace})


def cmd_trace_bind(args, ci: ResearchCI):
    from .provenance_guard import candidate_bindings_from_trace, verify_binding
    trace = load_trace(args.trace_file)
    binding = candidate_bindings_from_trace(args.claim_id, trace, args.select_id or None)
    verdict = verify_binding(args.claim_id, args.claim_text, trace, binding)
    ci.ws.save_mcp_trace(trace)
    ci.ws.save_binding(binding)
    ci.ws.ledger.append("claim.evidence_bound", args.claim_id, {
        "binding_id": binding.binding_id, "binding_digest": binding.digest,
        "trace_id": trace.trace_id, "verdict": verdict.status,
    })
    _print_json({"binding": binding.to_dict(), "verdict": verdict.to_dict()})


def _load_trace_as_lineage(trace_path: str):
    from .lineage import LineageGraph, LineageArtifact, LineageEdge, ArtifactKind
    trace = load_trace(trace_path)
    graph = LineageGraph()
    observation_ids = []
    for idx, call in enumerate(trace.calls):
        if not call.openaire_ids:
            continue
        oid = f"obs:{trace.trace_id}:{idx}"
        graph.add(LineageArtifact(
            logical_id=oid, kind=ArtifactKind.OBSERVATION.value,
            content={"tool": call.tool_name, "result": call.result, "openaire_ids": list(call.openaire_ids)},
            specification={"trace_id": trace.trace_id, "call_index": idx},
            metadata={"provider": trace.provider, "connector": trace.connector, "synthetic": trace.synthetic},
        ))
        observation_ids.append(oid)
    if not observation_ids:
        raise ValueError("trace has no OpenAIRE-ID-bearing observations")
    claim_deps = [LineageEdge(x, trust=1.0, authority="observed") for x in observation_ids[:2]]
    graph.add(LineageArtifact(
        logical_id="claim:demo", kind=ArtifactKind.CLAIM.value,
        content={"text": "The persistent research claim is grounded in selected OpenAIRE observations."},
        specification={"method": "source-bound claim"}, dependencies=claim_deps,
    ))
    graph.add(LineageArtifact(
        logical_id="report:demo", kind=ArtifactKind.REPORT.value,
        content={"summary": "A report that reuses the verified claim."},
        specification={"method": "report synthesis"},
        dependencies=[LineageEdge("claim:demo", trust=0.95, authority="machine_proposed")],
    ))
    graph.add(LineageArtifact(
        logical_id="recommendation:demo", kind=ArtifactKind.RECOMMENDATION.value,
        content={"recommendation": "Downstream recommendation derived from the report."},
        specification={"method": "decision synthesis"},
        dependencies=[LineageEdge("report:demo", trust=0.95, authority="machine_proposed")],
    ))
    return trace, graph, observation_ids


def cmd_lineage_demo(args, ci: ResearchCI):
    from .crux import rank_cruxes
    from .trust import ActionPolicy, PolicyEngine
    trace, graph, observations = _load_trace_as_lineage(args.trace_file)
    before = graph.to_dict()
    changed = [observations[0]]
    plan = graph.mark_invalidated(changed)
    gate = PolicyEngine().evaluate(graph, "recommendation:demo", ActionPolicy("publish", minimum_path_trust=0.7))
    cruxes = [x.to_dict() for x in rank_cruxes(graph, ["recommendation:demo"])]
    ci.ws.save_lineage(args.graph_id, graph)
    ci.ws.ledger.append("lineage.invalidated", args.graph_id, {"changed": changed, **plan})
    _print_json({
        "graph_id": args.graph_id, "trace_id": trace.trace_id,
        "before_nodes": len(before["nodes"]), "changed": changed,
        "invalidation": plan, "publish_gate": gate.to_dict(), "cruxes": cruxes[:5],
    })


def cmd_checkpoint(args, ci: ResearchCI):
    from .canonical import canonical_json_bytes
    from .merkle import merkle_root, MerkleCheckpoint
    from .ledger import utc_now
    events = ci.ws.ledger.events()
    leaves = [canonical_json_bytes(e) for e in events]
    cp = MerkleCheckpoint(len(leaves), merkle_root(leaves), utc_now())
    if args.private_key:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        except ImportError as exc:
            raise SystemExit("install patala-research-ci[crypto]") from exc
        key = Ed25519PrivateKey.from_private_bytes(Path(args.private_key).read_bytes())
        cp = cp.with_signature(args.key_id, key.sign(cp.signing_bytes()))
    cid = args.id or f"checkpoint:{len(events)}"
    ci.ws.save_checkpoint(cid, cp)
    _print_json({"checkpoint_id": cid, **cp.to_dict()})


def cmd_keygen(args, ci: ResearchCI):
    from .attestation import generate_ed25519_keypair
    priv, pub = generate_ed25519_keypair(args.private, args.public)
    _print_json({"private": str(priv), "public": str(pub)})


def cmd_attest(args, ci: ResearchCI):
    from .attestation import statement_for, sign_statement
    payload = json.loads(Path(args.predicate_json).read_text(encoding="utf-8"))
    statement = statement_for(args.subject_name, args.subject_digest, args.predicate_type, payload)
    env = sign_statement(statement, args.private_key, args.key_id)
    aid = args.id or f"attestation:{statement.digest.split(':')[-1][:16]}"
    ci.ws.save_attestation(aid, env)
    ci.ws.ledger.append("attestation.created", args.subject_name, {"attestation_id": aid, "statement_digest": statement.digest})
    _print_json({"attestation_id": aid, "statement": statement.to_dict(), "envelope": env.to_dict()})


def cmd_lineage_export(args, ci: ResearchCI):
    graph = ci.ws.load_lineage(args.graph_id)
    if args.format == "openlineage":
        from .openlineage_export import export_events
        data = export_events(graph)
    else:
        from .prov_export import export_prov_jsonld
        data = export_prov_jsonld(graph)
    Path(args.out).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_json({"graph_id": args.graph_id, "format": args.format, "out": args.out})


def main(argv: list[str] | None = None):
    args = build_parser().parse_args(argv)
    ws = Workspace(args.workspace)
    ci = ResearchCI(ws)
    if args.cmd == "track": cmd_track(args, ci)
    elif args.cmd == "verify": cmd_verify(args, ci)
    elif args.cmd == "resolve": _print_json(ci.resolve_computable(args.obligation_id))
    elif args.cmd == "log": _print_json(ws.ledger.events()[-args.tail:])
    elif args.cmd == "verify-ledger":
        ok, reason = ws.ledger.verify(); _print_json({"ok": ok, "reason": reason, "state_digest": ws.ledger.state_digest()})
        raise SystemExit(0 if ok else 2)
    elif args.cmd == "list": _print_json({"analyses": ws.list_analyses(), "obligations": ws.list_obligations()})
    elif args.cmd == "export": print(export_ro_crate(ws, args.analysis_id, args.out))
    elif args.cmd == "demo": cmd_demo(args, ci)
    elif args.cmd == "mcp-import": cmd_mcp_import(args, ci)
    elif args.cmd == "mcp-list": _print_json(ws.list_mcp_traces())
    elif args.cmd == "mcp-tools": cmd_mcp_tools(args, ci)
    elif args.cmd == "mcp-call": cmd_mcp_call(args, ci)
    elif args.cmd == "trace-bind": cmd_trace_bind(args, ci)
    elif args.cmd == "lineage-demo": cmd_lineage_demo(args, ci)
    elif args.cmd == "checkpoint": cmd_checkpoint(args, ci)
    elif args.cmd == "keygen": cmd_keygen(args, ci)
    elif args.cmd == "attest": cmd_attest(args, ci)
    elif args.cmd == "lineage-export": cmd_lineage_export(args, ci)
    elif args.cmd == "serve": serve_dashboard(args.workspace, args.host, args.port)


if __name__ == "__main__":
    main()
