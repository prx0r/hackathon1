from __future__ import annotations

"""W3C-PROV-inspired JSON-LD export for lineage artifacts and derivations."""

from .lineage import LineageGraph


def export_prov_jsonld(graph: LineageGraph) -> dict:
    context = {
        "prov": "http://www.w3.org/ns/prov#",
        "patala": "https://patala.dev/ns#",
        "id": "@id",
        "type": "@type",
    }
    nodes = []
    for node_id in sorted(graph.nodes):
        node = graph.nodes[node_id]
        nodes.append({
            "id": f"patala:{node.logical_id}",
            "type": "prov:Entity",
            "patala:kind": node.kind,
            "patala:digest": node.content_digest,
            "patala:state": node.state,
            "prov:wasDerivedFrom": [{"id": f"patala:{d.upstream_id}"} for d in node.dependencies],
        })
    return {"@context": context, "@graph": nodes}
