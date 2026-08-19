"""OpenAIRE Graph V3 adapter — fetch, normalize, canonicalize."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

import httpx


V3_BASE = "https://api.openaire.eu/graph/v3"

# Fields to exclude from canonicalization (timestamps that always change)
_EXCLUDE_FIELDS = {"dateOfCollection", "lastUpdateTimeStamp"}


@dataclass
class NormalizedRecord:
    """A canonical OpenAIRE record with stable identity."""
    id: str
    entity_type: str  # research-product, organization, project, person
    canonical: dict   # sorted, cleaned fields
    digest: str       # sha256 of canonical JSON
    fetched_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "canonical": self.canonical,
            "digest": self.digest,
            "fetched_at": self.fetched_at,
        }


def _canonicalize_record(record: dict) -> dict:
    """Normalize an OpenAIRE record for deterministic comparison.

    - Remove volatile timestamp fields
    - Sort keys recursively
    - Strip None values
    """
    def clean(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in sorted(obj.items())
                    if k not in _EXCLUDE_FIELDS and v is not None}
        if isinstance(obj, list):
            return [clean(item) for item in obj]
        return obj

    return clean(record)


def _digest(obj: dict) -> str:
    """SHA-256 of JCS-canonical JSON."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _make_id(record: dict, entity_type: str) -> str:
    """Extract or construct a stable entity ID."""
    # OpenAIRE V3 records have "id" at top level
    raw_id = record.get("id", "")
    if raw_id:
        return f"openaire:{raw_id}"

    # Fallback: try DOIs or other PIDs
    pids = record.get("pids", [])
    for pid in pids:
        if pid.get("scheme") == "doi":
            return f"doi:{pid['value']}"

    # Last resort: hash the title
    title = record.get("mainTitle", record.get("title", ""))
    return f"openaire:hash:{_digest({'title': title, 'type': entity_type})[:16]}"


# Anti-cheat invariants (from QDW doctrine)
class SourceStatus:
    OK = "OK"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PARTIAL = "PARTIAL"
    ERROR = "ERROR"


class OpenAIREClient:
    """V3 Graph API client with normalization and caching."""

    def __init__(self, base_url: str = V3_BASE, timeout: int = 30):
        self.base_url = base_url
        self.client = httpx.Client(timeout=timeout)

    def search(
        self,
        entity_type: str = "research-products",
        search: str = "",
        filters: dict | None = None,
        page_size: int = 25,
        page: int = 1,
    ) -> tuple[dict, str]:
        """Search OpenAIRE V3. Returns (raw API response, source_status).

        Anti-cheat invariant: SOURCE FAILURE ≠ ZERO RESULTS.
        """
        params: dict[str, Any] = {
            "pageSize": page_size,
            "page": page,
        }
        if search:
            params["search"] = search
        if filters:
            for k, v in filters.items():
                params[k] = v

        url = f"{self.base_url}/{entity_type}"
        try:
            resp = self.client.get(url, params=params)
            resp.raise_for_status()
            return resp.json(), SourceStatus.OK
        except httpx.HTTPStatusError:
            return {"results": [], "header": {"numFound": 0}}, SourceStatus.SOURCE_UNAVAILABLE
        except httpx.ConnectError:
            return {"results": [], "header": {"numFound": 0}}, SourceStatus.SOURCE_UNAVAILABLE

    def fetch_records(
        self,
        entity_type: str = "research-products",
        search: str = "",
        filters: dict | None = None,
        page_size: int = 25,
        max_pages: int = 10,
    ) -> tuple[list[NormalizedRecord], str]:
        """Fetch and normalize records across multiple pages.

        Returns (records, source_status).
        Anti-cheat: never returns empty list on source failure without status.
        """
        records = []
        overall_status = SourceStatus.OK

        for page in range(1, max_pages + 1):
            data, status = self.search(entity_type, search, filters, page_size, page)
            if status != SourceStatus.OK:
                overall_status = status
                break

            results = data.get("results", [])
            if not results:
                break

            for rec in results:
                normalized = _canonicalize_record(rec)
                nid = _make_id(rec, entity_type)
                records.append(NormalizedRecord(
                    id=nid,
                    entity_type=entity_type,
                    canonical=normalized,
                    digest=_digest(normalized),
                    fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                ))

            # Check if we've got all results
            total = data.get("header", {}).get("numFound", 0)
            if page * page_size >= total:
                break

        return records, overall_status

    def fetch_single(self, entity_type: str, entity_id: str) -> NormalizedRecord | None:
        """Fetch a single entity by OpenAIRE ID."""
        url = f"{self.base_url}/{entity_type}/{entity_id}"
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None
            rec = results[0]
            normalized = _canonicalize_record(rec)
            return NormalizedRecord(
                id=f"openaire:{entity_id}",
                entity_type=entity_type,
                canonical=normalized,
                digest=_digest(normalized),
                fetched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )
        except httpx.HTTPStatusError:
            return None

    def close(self):
        self.client.close()
