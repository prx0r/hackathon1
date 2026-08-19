"""ResolutionPlan — frozen, versioned verification plans for proof obligations.

Adapted from QDW VerificationPlan: a plan defines what must be demonstrated
before a claim can return to CURRENT. Plans are immutable once created;
changing the plan creates a new version with a new hash.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResolutionCheck:
    """A single check that must pass to resolve an obligation."""
    id: str
    description: str
    check_type: str  # rerun_query, recompute_statistic, compare_threshold, human_review
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "check_type": self.check_type,
            "params": self.params,
        }


@dataclass
class ResolutionPlan:
    """Frozen, versioned plan for resolving a proof obligation.

    Once created with a plan_hash, the acceptance criteria cannot change
    without creating a new plan (which is itself an event).
    """
    plan_id: str
    version: str = "1"
    description: str = ""
    checks: list[ResolutionCheck] = field(default_factory=list)
    acceptance: dict = field(default_factory=dict)  # frozen acceptance criteria
    plan_hash: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.plan_hash:
            self.plan_hash = self._compute_hash()
        if not self.created_at:
            self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _compute_hash(self) -> str:
        """Deterministic hash of the plan contents."""
        contents = {
            "plan_id": self.plan_id,
            "version": self.version,
            "checks": [c.to_dict() for c in self.checks],
            "acceptance": self.acceptance,
        }
        canonical = json.dumps(contents, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "version": self.version,
            "description": self.description,
            "checks": [c.to_dict() for c in self.checks],
            "acceptance": self.acceptance,
            "plan_hash": self.plan_hash,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ResolutionPlan:
        return cls(
            plan_id=d["plan_id"],
            version=d.get("version", "1"),
            description=d.get("description", ""),
            checks=[ResolutionCheck(**c) for c in d.get("checks", [])],
            acceptance=d.get("acceptance", {}),
            plan_hash=d.get("plan_hash", ""),
            created_at=d.get("created_at", ""),
        )


def create_recompute_plan(claim_id: str, query: dict) -> ResolutionPlan:
    """Create a plan for recomputing a claim after source change."""
    return ResolutionPlan(
        plan_id=f"recompute:{claim_id}",
        version="1",
        description=f"Recompute claim {claim_id} against current graph state",
        checks=[
            ResolutionCheck(
                id="rerun-query",
                description="Rerun the original OpenAIRE query",
                check_type="rerun_query",
                params={"query": query},
            ),
            ResolutionCheck(
                id="recompute-statistic",
                description="Recompute the derived statistic or conclusion",
                check_type="recompute_statistic",
            ),
            ResolutionCheck(
                id="compare-threshold",
                description="Compare new result against previous; check if conclusion changes",
                check_type="compare_threshold",
                params={"threshold": 0.05},
            ),
        ],
        acceptance={
            "type": "analysis_recompute",
            "expected": {
                "conclusion_stable": True,
                "max_effect_change": 0.05,
            },
        },
    )


def create_human_review_plan(claim_id: str, reason: str) -> ResolutionPlan:
    """Create a plan requiring human judgment."""
    return ResolutionCheck(
        id="human-judgment",
        description=f"Human review required: {reason}",
        check_type="human_review",
    ) and ResolutionPlan(  # type: ignore
        plan_id=f"human-review:{claim_id}",
        version="1",
        description=f"Human review for {claim_id}: {reason}",
        checks=[
            ResolutionCheck(
                id="human-judgment",
                description=f"Human review: {reason}",
                check_type="human_review",
            ),
        ],
        acceptance={
            "type": "human_adjudication",
            "expected": {
                "adjudicator_orcid": "required",
                "decision_recorded": True,
            },
        },
    )
