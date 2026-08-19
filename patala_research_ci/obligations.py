"""Proof obligations — machine-readable re-verification tasks.

Adapted from QDW ReviewFinding: obligations carry frozen acceptance criteria
that cannot be weakened after creation. Changing the criterion creates a new
obligation (which is itself an event).
"""

from __future__ import annotations

import hashlib
import json
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
    """A machine-readable obligation to re-verify a claim.

    Carries frozen acceptance criteria (adapted from QDW):
    the criterion is hashed at creation time and cannot be silently
    weakened later.
    """
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

    # Frozen acceptance criteria (QDW-inspired)
    acceptance: dict = field(default_factory=dict)
    acceptance_hash: str = ""

    def __post_init__(self):
        if self.acceptance and not self.acceptance_hash:
            self.acceptance_hash = self._hash_acceptance()

    def _hash_acceptance(self) -> str:
        canonical = json.dumps(self.acceptance, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()

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
            "acceptance": self.acceptance,
            "acceptance_hash": self.acceptance_hash,
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


def _frozen_acceptance(impact: ClaimImpact) -> dict:
    """Create frozen acceptance criteria at obligation creation time.

    These criteria cannot be weakened after the fact.
    """
    if impact.status == ClaimStatus.HUMAN_REVIEW:
        return {
            "type": "human_adjudication",
            "required": ["adjudicator_orcid", "decision_recorded", "evidence_cited"],
        }
    if impact.status == ClaimStatus.RECOMPUTE:
        return {
            "type": "analysis_recompute",
            "required": ["rerun_query", "recompute_statistic", "compare_result"],
            "constraints": {
                "conclusion_must_be_stated": True,
                "evidence_must_be_cited": True,
            },
        }
    return {
        "type": "recheck_evidence",
        "required": ["verify_source", "compare_versions"],
    }


# Counter for sequential PO IDs
_po_counter = 0


def _next_po_id() -> str:
    global _po_counter
    _po_counter += 1
    return f"PO-{_po_counter:04d}"


def generate_obligations(report: ImpactReport) -> list[ProofObligation]:
    """Generate proof obligations from an impact report.

    Each obligation carries frozen acceptance criteria that cannot
    be silently weakened after creation.
    """
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

        # Frozen acceptance criteria
        acceptance = _frozen_acceptance(impact)

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
            acceptance=acceptance,
        )
        obligations.append(po)

    return obligations
