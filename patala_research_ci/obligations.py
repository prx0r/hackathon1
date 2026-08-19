"""Proof obligations — machine-readable re-verification tasks."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .impact import ImpactReport, ClaimImpact
from .tracked import ClaimStatus


class ResolutionClass(str):
    AUTOMATIC_RECOMPUTE = "AUTOMATIC_RECOMPUTE"
    AGENT_RESEARCH = "AGENT_RESEARCH"
    HUMAN_VALIDATION = "HUMAN_VALIDATION"
    NO_ACTION = "NO_ACTION"


@dataclass
class ProofObligation:
    """A machine-readable obligation to re-verify a claim."""
    id: str
    claim_id: str
    analysis_id: str
    reason: str
    change_ref: str  # reference to what changed
    recommended_action: str
    resolution_class: str
    status: str = "OPEN"  # OPEN, RESOLVED, DISMISSED
    created_at: str = ""
    resolved_at: str | None = None
    resolution_note: str | None = None

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "claim_id": self.claim_id,
            "analysis_id": self.analysis_id,
            "reason": self.reason,
            "change_ref": self.change_ref,
            "recommended_action": self.recommended_action,
            "resolution_class": self.resolution_class,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.resolved_at:
            d["resolved_at"] = self.resolved_at
        if self.resolution_note:
            d["resolution_note"] = self.resolution_note
        return d


def _classify_resolution(impact: ClaimImpact) -> str:
    """Determine how a proof obligation should be resolved."""
    if impact.status == ClaimStatus.HUMAN_REVIEW:
        return ResolutionClass.HUMAN_VALIDATION
    if impact.status == ClaimStatus.RECOMPUTE:
        return ResolutionClass.AUTOMATIC_RECOMPUTE
    if impact.status == ClaimStatus.SOURCE_CHANGED:
        return ResolutionClass.AUTOMATIC_RECOMPUTE
    return ResolutionClass.NO_ACTION


def _recommend_action(impact: ClaimImpact) -> str:
    """What action should be taken."""
    if impact.status == ClaimStatus.HUMAN_REVIEW:
        return "HUMAN_REVIEW"
    if impact.status == ClaimStatus.RECOMPUTE:
        return "RECOMPUTE"
    if impact.status == ClaimStatus.SOURCE_CHANGED:
        return "RECHECK_EVIDENCE"
    return "NONE"


# Counter for sequential PO IDs
_po_counter = 0


def _next_po_id() -> str:
    global _po_counter
    _po_counter += 1
    return f"PO-{_po_counter:04d}"


def generate_obligations(report: ImpactReport) -> list[ProofObligation]:
    """Generate proof obligations from an impact report."""
    obligations = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for impact in report.claim_impacts:
        # Skip unaffected claims
        if impact.status == ClaimStatus.CURRENT:
            continue

        resolution_class = _classify_resolution(impact)
        action = _recommend_action(impact)

        # Build change reference
        change_refs = impact.affected_by
        change_ref = "; ".join(change_refs[:3])  # first 3
        if len(change_refs) > 3:
            change_ref += f"; +{len(change_refs) - 3} more"

        po = ProofObligation(
            id=_next_po_id(),
            claim_id=impact.claim_id,
            analysis_id=report.analysis_id,
            reason=impact.reason,
            change_ref=change_ref,
            recommended_action=action,
            resolution_class=resolution_class,
            status="OPEN",
            created_at=now,
        )
        obligations.append(po)

    return obligations
