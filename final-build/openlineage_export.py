from __future__ import annotations

"""Interoperability export using OpenLineage's Job/Run/Dataset conceptual model.

The emitted JSON is intentionally a small subset for transport/interchange and does
not claim certification against every OpenLineage facet schema.
"""

from typing import Any
import uuid
from .ledger import utc_now
from .lineage import LineageGraph

PRODUCER = "https://github.com/prx0r/hackathon1"
SCHEMA_URL = "https://openlineage.io/spec/2-0-2/OpenLineage.json"


def export_events(graph: LineageGraph, namespace: str = "patala") -> list[dict[str, Any]]:
    events = []
    for node_id in sorted(graph.nodes):
        node = graph.nodes[node_id]
        inputs = []
        for dep in node.dependencies:
            upstream = graph.nodes[dep.upstream_id]
            inputs.append({"namespace": namespace, "name": upstream.logical_id, "facets": {"patala": {"_producer": PRODUCER, "_schemaURL": "https://patala.dev/openlineage/facet/v1", "digest": upstream.content_digest}}})
        output = {"namespace": namespace, "name": node.logical_id, "facets": {"patala": {"_producer": PRODUCER, "_schemaURL": "https://patala.dev/openlineage/facet/v1", "digest": node.content_digest, "executionKey": node.execution_key}}}
        events.append({
            "eventType": "COMPLETE",
            "eventTime": utc_now(),
            "run": {"runId": str(uuid.uuid4())},
            "job": {"namespace": namespace, "name": f"derive:{node.kind}"},
            "inputs": inputs,
            "outputs": [output],
            "producer": PRODUCER,
            "schemaURL": SCHEMA_URL,
        })
    return events
