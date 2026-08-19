"""Attack catalog — adversarial test cases for Research CI.

Adapted from QDW AttackCatalog: versioned attack definitions that test
specific failure modes. Each attack has a desired property that must hold.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Attack:
    """An adversarial test case."""
    id: str
    name: str
    description: str
    category: str  # source, diff, impact, obligation
    desired_property: str  # what should happen
    input_fixture: str = ""  # path to test fixture

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "desired_property": self.desired_property,
            "input_fixture": self.input_fixture,
        }


# The attack catalog
ATTACKS: list[Attack] = [
    Attack(
        id="A01",
        name="source_timeout",
        description="OpenAIRE API returns 500 or times out",
        category="source",
        desired_property="SOURCE FAILURE ≠ ZERO RESULTS — snapshot records SOURCE_UNAVAILABLE, no diff computed",
    ),
    Attack(
        id="A02",
        name="response_truncated",
        description="OpenAIRE returns partial page (network interruption)",
        category="source",
        desired_property="PARTIAL PAGE ≠ COMPLETE RESULT SET — snapshot records partial status",
    ),
    Attack(
        id="A03",
        name="duplicate_records",
        description="Same entity appears multiple times in results",
        category="diff",
        desired_property="Deduplication before diff — duplicates collapsed by ID",
    ),
    Attack(
        id="A04",
        name="cosmetic_title_change",
        description="Only whitespace/punctuation in title changed",
        category="diff",
        desired_property="COSMETIC CHANGE ≠ MATERIAL CHANGE — classified as cosmetic, no proof obligation",
    ),
    Attack(
        id="A05",
        name="unrelated_affiliation_change",
        description="Author affiliation changed but claim has no affiliation dependency",
        category="impact",
        desired_property="Claim unaffected if no dependency path to changed field",
    ),
    Attack(
        id="A06",
        name="supporting_relation_removed",
        description="A relation that a claim depends on is absent in new snapshot",
        category="impact",
        desired_property="Claim flagged RECOMPUTE with proof obligation identifying the exact removed relation",
    ),
    Attack(
        id="A07",
        name="retraction_event",
        description="A record is retracted/corrected in new snapshot",
        category="impact",
        desired_property="Claim flagged HUMAN_REVIEW — retraction requires human judgment, not auto-recompute",
    ),
    Attack(
        id="A08",
        name="id_canonicalization_changed",
        description="Entity ID format changed (e.g. DOI normalization)",
        category="diff",
        desired_property="Identity normalization handles both formats — not counted as add+remove pair",
    ),
    Attack(
        id="A09",
        name="result_ordering_changed",
        description="Results returned in different order but same content",
        category="diff",
        desired_property="IDENTICAL snapshot digest after canonical sorting",
    ),
    Attack(
        id="A10",
        name="new_result_changes_aggregate",
        description="One new record changes a proportion/statistic",
        category="impact",
        desired_property="Claim flagged RECOMPUTE with reason showing new record affected the aggregate",
    ),
    Attack(
        id="A11",
        name="empty_results_not_stale",
        description="New query returns 0 results but old had 50 (source error, not deletion)",
        category="source",
        desired_property="SOURCE_UNAVAILABLE state prevents false mass-staleness",
    ),
    Attack(
        id="A12",
        name="deterministic_recompute",
        description="Same inputs + same plan → same receipt hash",
        category="obligation",
        desired_property="R2: deterministic — replay produces identical ImpactReport and receipt",
    ),
]


def get_attack(attack_id: str) -> Attack | None:
    """Get an attack by ID."""
    for a in ATTACKS:
        if a.id == attack_id:
            return a
    return None


def list_attacks(category: str | None = None) -> list[Attack]:
    """List attacks, optionally filtered by category."""
    if category:
        return [a for a in ATTACKS if a.category == category]
    return list(ATTACKS)
