"""Impact analysis — match diff changes against claim dependencies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .diff import SemanticDiff, ChangeKind
from .tracked import TrackedClaim, ClaimStatus, Dependency, DepKind


@dataclass
class ClaimImpact:
    """Impact assessment for a single claim."""
    claim_id: str
    status: ClaimStatus
    affected_by: list[str] = field(default_factory=list)  # entity/change IDs that caused this
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "status": self.status.value,
            "affected_by": self.affected_by,
            "reason": self.reason,
        }


@dataclass
class ImpactReport:
    """Complete impact report for an analysis."""
    analysis_id: str
    diff_summary: dict = field(default_factory=dict)
    claim_impacts: list[ClaimImpact] = field(default_factory=list)
    unaffected: list[str] = field(default_factory=list)
    source_changed: list[str] = field(default_factory=list)
    recompute: list[str] = field(default_factory=list)
    human_review: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "analysis_id": self.analysis_id,
            "diff_summary": self.diff_summary,
            "claim_impacts": [c.to_dict() for c in self.claim_impacts],
            "summary": {
                "unaffected": self.unaffected,
                "source_changed": self.source_changed,
                "recompute": self.recompute,
                "human_review": self.human_review,
            },
        }


def _dep_matches_entity(dep: Dependency, entity_id: str) -> bool:
    """Check if a dependency references this entity."""
    if dep.kind == DepKind.ENTITY:
        return dep.ref == entity_id
    if dep.kind == DepKind.RELATION:
        return dep.source == entity_id or dep.target == entity_id
    if dep.kind == DepKind.FIELD:
        return dep.ref == entity_id
    return False


def _dep_matches_field_change(dep: Dependency, entity_id: str, field_name: str) -> bool:
    """Check if a dependency is affected by a field change."""
    if dep.kind == DepKind.FIELD:
        return dep.ref == entity_id and dep.field == field_name
    if dep.kind == DepKind.RELATION:
        # Relations are stored as field changes
        return dep.source == entity_id
    return False


def analyze_impact(
    analysis_id: str,
    claims: list[TrackedClaim],
    diff: SemanticDiff,
) -> ImpactReport:
    """Analyze which claims are affected by a diff.

    This is the core of Research CI — matching upstream changes
    against downstream claim dependencies.
    """
    report = ImpactReport(analysis_id=analysis_id)
    report.diff_summary = diff.to_dict().get("summary", {})

    # Build index of changed entities
    changed_entities: dict[str, list] = {}  # entity_id -> [FieldChange]
    removed_entities: set[str] = set()
    added_entities: set[str] = set()

    for ed in diff.entity_diffs:
        if ed.added:
            added_entities.add(ed.entity_id)
        elif ed.removed:
            removed_entities.add(ed.entity_id)
        elif ed.changed_fields:
            changed_entities[ed.entity_id] = ed.changed_fields

    for claim in claims:
        affected_by = []
        is_affected = False

        for dep in claim.dependencies:
            # Check if any dependency entity was removed
            if _dep_matches_entity(dep, None) and dep.ref in removed_entities:
                affected_by.append(f"entity_removed:{dep.ref}")
                is_affected = True

            # Check if any dependency entity was added (supporting evidence)
            if _dep_matches_entity(dep, None) and dep.ref in added_entities:
                affected_by.append(f"entity_added:{dep.ref}")
                # Addition doesn't make claim stale — it's new evidence
                # Only flag if the claim's meaning changes

            # Check if any dependency field changed
            for eid, changes in changed_entities.items():
                for change in changes:
                    if _dep_matches_field_change(dep, eid, change.field):
                        affected_by.append(
                            f"field_changed:{eid}:{change.field} "
                            f"({change.materiality})"
                        )
                        is_affected = True

        if is_affected:
            # Classify based on materiality
            has_relation_change = any("RELATION" in ab for ab in affected_by)
            has_retraction = any("RETRACTION" in ab for ab in affected_by)

            if has_retraction:
                status = ClaimStatus.HUMAN_REVIEW
                reason = "Source record retracted or corrected"
            elif has_relation_change:
                status = ClaimStatus.RECOMPUTE
                reason = "Supporting relation changed or removed"
            else:
                status = ClaimStatus.SOURCE_CHANGED
                reason = "Metadata changed on dependent record"

            impact = ClaimImpact(
                claim_id=claim.claim_id,
                status=status,
                affected_by=affected_by,
                reason=reason,
            )
            report.claim_impacts.append(impact)

            if status == ClaimStatus.HUMAN_REVIEW:
                report.human_review.append(claim.claim_id)
            else:
                report.recompute.append(claim.claim_id)
                report.source_changed.append(claim.claim_id)
        else:
            report.unaffected.append(claim.claim_id)

    return report
