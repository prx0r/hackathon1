"""Ledger — thin wrapper around Pāṭala's append-only event store."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

# Try to import from Pāṭala; fall back to local implementation
try:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "openpatalaproject"))
    from patala.events import EventStore
    from patala.hashing import uuid7
    _HAS_PATALA = True
except ImportError:
    _HAS_PATALA = False


class LocalEventStore:
    """Minimal local event store if Pāṭala isn't available."""

    def __init__(self, store_dir: Path):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.events_file = self.store_dir / "events.jsonl"
        self._cursor = self._count()

    def _count(self) -> int:
        if not self.events_file.exists():
            return 0
        with open(self.events_file) as f:
            return sum(1 for _ in f)

    def append(self, event_type: str, entity_ids: list[str],
               payload: dict, **kwargs) -> dict:
        import hashlib
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        event_id = f"PTEVT_{int(time.time()*1000):012x}"
        payload_bytes = json.dumps(payload, sort_keys=True, default=str).encode()
        payload_digest = hashlib.sha256(payload_bytes).hexdigest()

        event = {
            "event_id": event_id,
            "event_type": event_type,
            "entity_ids": entity_ids,
            "recorded_at": now,
            "payload": payload,
            "payload_digest": {"algorithm": "sha256", "value": payload_digest},
            "cursor": self._cursor,
        }
        with open(self.events_file, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")
        self._cursor += 1
        return event

    @property
    def cursor(self) -> int:
        return self._cursor


class ResearchCILedger:
    """Append-only event ledger for Research CI operations."""

    def __init__(self, store_dir: str | Path):
        self.store_dir = Path(store_dir)
        if _HAS_PATALA:
            self.store = EventStore(self.store_dir)
        else:
            self.store = LocalEventStore(self.store_dir)

    def record_track(self, analysis_id: str, query: dict,
                     record_count: int, snapshot_digest: str) -> Any:
        """Record a tracking event."""
        return self.store.append(
            event_type="AnalysisTracked",
            entity_ids=[analysis_id],
            payload={
                "query": query,
                "record_count": record_count,
                "snapshot_digest": snapshot_digest,
            },
        )

    def record_verify(self, analysis_id: str, diff_summary: dict,
                      claim_count: int, affected_count: int) -> Any:
        """Record a verification event."""
        return self.store.append(
            event_type="AnalysisVerified",
            entity_ids=[analysis_id],
            payload={
                "diff_summary": diff_summary,
                "claim_count": claim_count,
                "affected_count": affected_count,
            },
        )

    def record_obligation(self, obligation: dict) -> Any:
        """Record a proof obligation event."""
        return self.store.append(
            event_type="ProofObligationEmitted",
            entity_ids=[obligation.get("claim_id", "")],
            payload=obligation,
        )

    def record_resolution(self, obligation_id: str, resolution: str,
                          note: str | None = None) -> Any:
        """Record a proof obligation resolution."""
        return self.store.append(
            event_type="ProofObligationResolved",
            entity_ids=[obligation_id],
            payload={
                "obligation_id": obligation_id,
                "resolution": resolution,
                "note": note,
            },
        )

    def log(self, limit: int = 20) -> list[dict]:
        """Read recent events."""
        events = []
        events_file = self.store_dir / "events.jsonl"
        if not events_file.exists():
            return events
        with open(events_file) as f:
            lines = f.readlines()
        for line in lines[-limit:]:
            events.append(json.loads(line))
        return events
