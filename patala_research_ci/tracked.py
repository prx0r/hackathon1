"""TrackedAnalysis and TrackedClaim — the core data model."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .openaire import NormalizedRecord, _digest


class ClaimStatus(str, Enum):
    CURRENT = "CURRENT"
    STALE = "STALE"
    SOURCE_CHANGED = "SOURCE_CHANGED"
    RECOMPUTE = "RECOMPUTE"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class DepKind(str, Enum):
    ENTITY = "entity"
    RELATION = "relation"
    FIELD = "field"


@dataclass
class Dependency:
    """A specific thing a claim depends on."""
    kind: DepKind
    ref: str | None = None
    source: str | None = None
    predicate: str | None = None
    target: str | None = None
    field: str | None = None

    def key(self) -> str:
        if self.kind == DepKind.ENTITY:
            return f"entity:{self.ref}"
        if self.kind == DepKind.RELATION:
            return f"relation:{self.source}:{self.predicate}:{self.target}"
        if self.kind == DepKind.FIELD:
            return f"field:{self.ref}:{self.field}"
        return str(self)

    def to_dict(self) -> dict:
        d: dict[str, str] = {"kind": self.kind.value}
        if self.ref: d["ref"] = self.ref
        if self.source: d["source"] = self.source
        if self.predicate: d["predicate"] = self.predicate
        if self.target: d["target"] = self.target
        if self.field: d["field"] = self.field
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Dependency:
        return cls(
            kind=DepKind(d["kind"]),
            ref=d.get("ref"),
            source=d.get("source"),
            predicate=d.get("predicate"),
            target=d.get("target"),
            field=d.get("field"),
        )


@dataclass
class TrackedClaim:
    """A conclusion with explicit dependencies on OpenAIRE records/relations."""
    claim_id: str
    text: str
    dependencies: list[Dependency] = field(default_factory=list)
    status: ClaimStatus = ClaimStatus.CURRENT
    created_at: str = ""
    verified_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "text": self.text,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "status": self.status.value,
            "created_at": self.created_at,
            "verified_at": self.verified_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> TrackedClaim:
        return cls(
            claim_id=d["claim_id"],
            text=d["text"],
            dependencies=[Dependency.from_dict(dep) for dep in d.get("dependencies", [])],
            status=ClaimStatus(d.get("status", "CURRENT")),
            created_at=d.get("created_at", ""),
            verified_at=d.get("verified_at"),
        )


@dataclass
class TrackedAnalysis:
    """A research analysis tracked against OpenAIRE."""
    analysis_id: str
    title: str
    source_provider: str = "openaire"
    source_api: str = "v3"
    query: dict = field(default_factory=dict)
    observed_at: str = ""
    source_version: str | None = None
    result_ids: list[str] = field(default_factory=list)
    snapshot_digest: str = ""
    claims: list[str] = field(default_factory=list)  # claim IDs
    snapshots: dict[str, dict] = field(default_factory=dict)  # version -> {id: NormalizedRecord.to_dict()}

    def to_dict(self) -> dict:
        return {
            "analysis_id": self.analysis_id,
            "title": self.title,
            "source": {"provider": self.source_provider, "api": self.source_api},
            "query": self.query,
            "observed_at": self.observed_at,
            "source_version": self.source_version,
            "result_ids": self.result_ids,
            "snapshot_digest": self.snapshot_digest,
            "claims": self.claims,
            "snapshots": self.snapshots,
        }

    @classmethod
    def from_dict(cls, d: dict) -> TrackedAnalysis:
        source = d.get("source", {})
        return cls(
            analysis_id=d["analysis_id"],
            title=d["title"],
            source_provider=source.get("provider", "openaire"),
            source_api=source.get("api", "v3"),
            query=d.get("query", {}),
            observed_at=d.get("observed_at", ""),
            source_version=d.get("source_version"),
            result_ids=d.get("result_ids", []),
            snapshot_digest=d.get("snapshot_digest", ""),
            claims=d.get("claims", []),
            snapshots=d.get("snapshots", {}),
        )

    @classmethod
    def create(cls, analysis_id: str, title: str, query: dict,
               records: list[NormalizedRecord], version: str | None = None) -> TrackedAnalysis:
        """Create a new tracked analysis from fetched records."""
        snapshot = {r.id: r.to_dict() for r in records}
        result_ids = [r.id for r in records]

        # Compute snapshot digest
        snapshot_bytes = json.dumps(result_ids, sort_keys=True).encode()
        snapshot_digest = "sha256:" + hashlib.sha256(snapshot_bytes).hexdigest()

        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return cls(
            analysis_id=analysis_id,
            title=title,
            query=query,
            observed_at=now,
            source_version=version,
            result_ids=result_ids,
            snapshot_digest=snapshot_digest,
            snapshots={version or "initial": snapshot},
        )
