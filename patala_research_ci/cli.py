"""CLI interface for Pāṭala Research CI."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .openaire import OpenAIREClient, SourceStatus
from .tracked import TrackedAnalysis, TrackedClaim, ClaimStatus, Dependency, DepKind
from .diff import compute_diff
from .impact import analyze_impact
from .obligations import generate_obligations
from .ledger import ResearchCILedger


DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"


def cmd_track(args):
    """Track an analysis against OpenAIRE."""
    client = OpenAIREClient()
    ledger = ResearchCILedger(DEFAULT_DATA_DIR / "ledger")

    print(f"Fetching from OpenAIRE V3...")
    records, status = client.fetch_records(
        entity_type=args.entity or "research-products",
        search=args.search or "",
        page_size=args.page_size or 25,
        max_pages=args.max_pages or 5,
    )
    client.close()

    if status != SourceStatus.OK:
        print(f"Source status: {status}")
        print("SOURCE FAILURE ≠ ZERO RESULTS — not recording empty snapshot")
        return

    if not records:
        print("No records found.")
        return

    # Create tracked analysis
    analysis_id = args.name or f"analysis:{int(time.time())}"
    query = {"search": args.search or "", "entity": args.entity or "research-products"}
    analysis = TrackedAnalysis.create(analysis_id, args.title or analysis_id, query, records)

    # Save
    analysis_file = DEFAULT_DATA_DIR / "analyses" / f"{analysis_id}.json"
    analysis_file.parent.mkdir(parents=True, exist_ok=True)
    with open(analysis_file, "w") as f:
        json.dump(analysis.to_dict(), f, indent=2, default=str)

    # Record event
    ledger.record_track(analysis_id, query, len(records), analysis.snapshot_digest)

    print(f"\nTrackedAnalysis created")
    print(f"  analysis_id: {analysis_id}")
    print(f"  records:     {len(records)}")
    print(f"  digest:      {analysis.snapshot_digest[:32]}...")
    print(f"  saved:       {analysis_file}")


def cmd_claim(args):
    """Add a tracked claim to an analysis."""
    analysis_file = DEFAULT_DATA_DIR / "analyses" / f"{args.analysis}.json"
    if not analysis_file.exists():
        print(f"Analysis not found: {args.analysis}")
        sys.exit(1)

    with open(analysis_file) as f:
        analysis = TrackedAnalysis.from_dict(json.load(f))

    # Create claim
    claim_id = args.claim_id or f"claim:{int(time.time())}"
    deps = []
    if args.depends:
        for dep_str in args.depends:
            # Parse "entity:openaire:xxx" or "relation:src:predicate:tgt"
            parts = dep_str.split(":", 1)
            if parts[0] == "entity":
                deps.append(Dependency(kind=DepKind.ENTITY, ref=parts[1]))
            elif parts[0] == "relation":
                # relation:source:predicate:target
                rp = parts[1].split(":")
                if len(rp) >= 3:
                    deps.append(Dependency(kind=DepKind.RELATION,
                                           source=rp[0], predicate=rp[1], target=rp[2]))
            elif parts[0] == "field":
                # field:entity_id:field_name
                fp = parts[1].split(":")
                if len(fp) >= 2:
                    deps.append(Dependency(kind=DepKind.FIELD, ref=fp[0], field=fp[1]))

    claim = TrackedClaim(
        claim_id=claim_id,
        text=args.text,
        dependencies=deps,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # Add to analysis
    analysis.claims.append(claim_id)
    analysis_file.parent.mkdir(parents=True, exist_ok=True)

    # Save claim separately
    claims_dir = DEFAULT_DATA_DIR / "claims"
    claims_dir.mkdir(parents=True, exist_ok=True)
    claim_file = claims_dir / f"{claim_id}.json"
    with open(claim_file, "w") as f:
        json.dump(claim.to_dict(), f, indent=2)

    # Update analysis
    with open(analysis_file, "w") as f:
        json.dump(analysis.to_dict(), f, indent=2, default=str)

    print(f"Claim added: {claim_id}")
    print(f"  text:         {args.text}")
    print(f"  dependencies: {len(deps)}")
    print(f"  analysis:     {args.analysis}")


def cmd_verify(args):
    """Verify an analysis against current OpenAIRE state."""
    analysis_file = DEFAULT_DATA_DIR / "analyses" / f"{args.analysis}.json"
    if not analysis_file.exists():
        print(f"Analysis not found: {args.analysis}")
        sys.exit(1)

    with open(analysis_file) as f:
        analysis = TrackedAnalysis.from_dict(json.load(f))

    # Get the old snapshot
    old_version = list(analysis.snapshots.keys())[-1] if analysis.snapshots else None
    old_snapshot = analysis.snapshots.get(old_version, {})
    if not old_snapshot:
        print("No snapshot found for analysis.")
        sys.exit(1)

    # Fetch current state
    print("Fetching current OpenAIRE state...")
    client = OpenAIREClient()
    records, status = client.fetch_records(
        entity_type=analysis.query.get("entity", "research-products"),
        search=analysis.query.get("search", ""),
        page_size=args.page_size or 25,
        max_pages=args.max_pages or 5,
    )
    client.close()

    if status != SourceStatus.OK:
        print(f"\nSource status: {status}")
        print("SOURCE FAILURE ≠ ZERO RESULTS — cannot verify against unavailable source")
        print("Marking snapshot as SOURCE_UNAVAILABLE, not computing diff")
        return

    new_snapshot = {r.id: r.to_dict() for r in records}
    new_version = time.strftime("%Y%m%d")
    new_digest = f"sha256:{__import__('hashlib').sha256(json.dumps(sorted(new_snapshot.keys())).encode()).hexdigest()}"

    print(f"\nGraph changes")
    print(f"{'─' * 40}")

    # Compute diff
    diff = compute_diff(old_snapshot, new_snapshot)

    print(f"  Old records:     {len(old_snapshot)}")
    print(f"  New records:     {len(new_snapshot)}")
    print(f"  Added:           {diff.added_count}")
    print(f"  Removed:         {diff.removed_count}")
    print(f"  Changed:         {diff.changed_count}")
    print(f"  Material changes: {diff.material_change_count}")

    # Load claims
    claims = []
    for claim_id in analysis.claims:
        claim_file = DEFAULT_DATA_DIR / "claims" / f"{claim_id}.json"
        if claim_file.exists():
            with open(claim_file) as f:
                claims.append(TrackedClaim.from_dict(json.load(f)))

    if not claims:
        print("\nNo tracked claims. Use 'patala claim add' to add claims.")
        # Save updated snapshot
        analysis.snapshots[new_version] = new_snapshot
        with open(analysis_file, "w") as f:
            json.dump(analysis.to_dict(), f, indent=2, default=str)
        return

    # Analyze impact
    report = analyze_impact(analysis_id=args.analysis, claims=claims, diff=diff)

    print(f"\nImpact")
    print(f"{'─' * 40}")
    for impact in report.claim_impacts:
        status_icon = {
            "SOURCE_CHANGED": "⚠️",
            "RECOMPUTE": "🔄",
            "HUMAN_REVIEW": "👤",
            "CURRENT": "✅",
        }.get(impact.status.value, "?")
        print(f"  {impact.claim_id:20s} {status_icon} {impact.status.value}")
        print(f"                       {impact.reason}")

    print(f"\n  Unaffected: {len(report.unaffected)}")
    print(f"  Recompute:  {len(report.recompute)}")
    print(f"  Human:      {len(report.human_review)}")

    # Generate proof obligations
    obligations = generate_obligations(report)
    if obligations:
        print(f"\nProof obligations")
        print(f"{'─' * 40}")
        for po in obligations:
            print(f"  {po.id}  {po.claim_id}")
            print(f"    Reason:   {po.reason}")
            print(f"    Action:   {po.recommended_action}")
            print(f"    Change:   {po.change_ref[:60]}")
            print()

        # Save obligations
        obs_dir = DEFAULT_DATA_DIR / "obligations"
        obs_dir.mkdir(parents=True, exist_ok=True)
        for po in obligations:
            po_file = obs_dir / f"{po.id}.json"
            with open(po_file, "w") as f:
                json.dump(po.to_dict(), f, indent=2)

    # Record verification event
    ledger = ResearchCILedger(DEFAULT_DATA_DIR / "ledger")
    ledger.record_verify(args.analysis, diff.to_dict().get("summary", {}),
                         len(claims), len(report.recompute) + len(report.human_review))

    for po in obligations:
        ledger.record_obligation(po.to_dict())

    # Save updated snapshot
    analysis.snapshots[new_version] = new_snapshot
    with open(analysis_file, "w") as f:
        json.dump(analysis.to_dict(), f, indent=2, default=str)

    print(f"Ledger updated.")


def cmd_log(args):
    """Show recent events."""
    ledger = ResearchCILedger(DEFAULT_DATA_DIR / "ledger")
    events = ledger.log(limit=args.limit or 20)

    if not events:
        print("No events recorded.")
        return

    for ev in events:
        print(f"  {ev.get('recorded_at', '?')}  {ev.get('event_type', '?')}  "
              f"{ev.get('entity_ids', [])}")


def cmd_list(args):
    """List tracked analyses."""
    analyses_dir = DEFAULT_DATA_DIR / "analyses"
    if not analyses_dir.exists():
        print("No analyses tracked.")
        return

    for f in sorted(analyses_dir.glob("*.json")):
        with open(f) as fh:
            data = json.load(fh)
        print(f"  {data.get('analysis_id', f.stem)}")
        print(f"    title:    {data.get('title', '?')}")
        print(f"    records:  {len(data.get('result_ids', []))}")
        print(f"    claims:   {len(data.get('claims', []))}")
        print(f"    observed: {data.get('observed_at', '?')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="patala",
        description="Pāṭala Research CI — continuous verification for scholarly knowledge graphs",
    )
    sub = parser.add_subparsers(dest="command")

    # track
    p_track = sub.add_parser("track", help="Track an analysis against OpenAIRE")
    p_track.add_argument("--name", help="Analysis ID")
    p_track.add_argument("--title", help="Human-readable title")
    p_track.add_argument("--search", help="Search query")
    p_track.add_argument("--entity", default="research-products", help="Entity type")
    p_track.add_argument("--page-size", type=int, default=25)
    p_track.add_argument("--max-pages", type=int, default=5)
    p_track.set_defaults(func=cmd_track)

    # claim
    p_claim = sub.add_parser("claim", help="Manage tracked claims")
    claim_sub = p_claim.add_subparsers(dest="claim_cmd")

    p_claim_add = claim_sub.add_parser("add", help="Add a claim")
    p_claim_add.add_argument("--analysis", required=True, help="Analysis ID")
    p_claim_add.add_argument("--claim-id", help="Claim ID")
    p_claim_add.add_argument("--text", required=True, help="Claim text")
    p_claim_add.add_argument("--depends", nargs="*", help="Dependencies (entity:X, relation:X:Y:Z, field:X:Y)")
    p_claim_add.set_defaults(func=cmd_claim)

    # verify
    p_verify = sub.add_parser("verify", help="Verify analysis against current state")
    p_verify.add_argument("analysis", help="Analysis ID")
    p_verify.add_argument("--page-size", type=int, default=25)
    p_verify.add_argument("--max-pages", type=int, default=5)
    p_verify.set_defaults(func=cmd_verify)

    # log
    p_log = sub.add_parser("log", help="Show recent events")
    p_log.add_argument("--limit", type=int, default=20)
    p_log.set_defaults(func=cmd_log)

    # list
    p_list = sub.add_parser("list", help="List tracked analyses")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
