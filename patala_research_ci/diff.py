"""Semantic diff between two snapshots of OpenAIRE records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Materiality taxonomy — not all changes matter equally
class ChangeKind(str):
    COSMETIC = "COSMETIC"
    IDENTITY = "IDENTITY"
    METADATA = "METADATA"
    RELATION = "RELATION"
    AVAILABILITY = "AVAILABILITY"
    VERSION = "VERSION"
    CORRECTION = "CORRECTION"
    RETRACTION = "RETRACTION"


# Fields considered cosmetic (never trigger proof obligations)
COSMETIC_FIELDS = {"formats", "sources", "contributors", "coverages"}

# Fields considered identity-level
IDENTITY_FIELDS = {"id", "originalIds", "pids"}

# Fields considered metadata
METADATA_FIELDS = {"mainTitle", "subTitle", "descriptions", "publisher",
                   "language", "publicationDate", "embargoEndDate", "subjects"}

# Fields that represent relations
RELATION_FIELDS = {"projects", "organizations", "communities", "collectedFrom"}

# Fields that represent availability
AVAILABILITY_FIELDS = {"bestAccessRight", "isGreen", "openAccessColor",
                       "isInDiamondJournal", "publiclyFunded"}


def classify_change(field_name: str) -> str:
    """Classify a field change by materiality."""
    if field_name in COSMETIC_FIELDS:
        return ChangeKind.COSMETIC
    if field_name in IDENTITY_FIELDS:
        return ChangeKind.IDENTITY
    if field_name in RELATION_FIELDS:
        return ChangeKind.RELATION
    if field_name in AVAILABILITY_FIELDS:
        return ChangeKind.AVAILABILITY
    if field_name in METADATA_FIELDS:
        return ChangeKind.METADATA
    return ChangeKind.METADATA  # default


@dataclass
class FieldChange:
    """A single field change within a record."""
    field: str
    old_value: Any
    new_value: Any
    materiality: str

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "materiality": self.materiality,
        }


@dataclass
class EntityDiff:
    """Changes to a single entity."""
    entity_id: str
    added: bool = False
    removed: bool = False
    changed_fields: list[FieldChange] = field(default_factory=list)

    @property
    def material_changes(self) -> list[FieldChange]:
        """Only non-cosmetic changes."""
        return [c for c in self.changed_fields if c.materiality != ChangeKind.COSMETIC]

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "added": self.added,
            "removed": self.removed,
            "changed_fields": [c.to_dict() for c in self.changed_fields],
        }


@dataclass
class SemanticDiff:
    """The complete diff between two snapshots."""
    entity_diffs: list[EntityDiff] = field(default_factory=list)
    added_count: int = 0
    removed_count: int = 0
    changed_count: int = 0
    material_change_count: int = 0

    def to_dict(self) -> dict:
        return {
            "entity_diffs": [d.to_dict() for d in self.entity_diffs],
            "summary": {
                "added": self.added_count,
                "removed": self.removed_count,
                "changed": self.changed_count,
                "material_changes": self.material_change_count,
            },
        }

    def changed_entity_ids(self) -> list[str]:
        """IDs of entities that were added, removed, or materially changed."""
        ids = []
        for d in self.entity_diffs:
            if d.added or d.removed or d.material_changes:
                ids.append(d.entity_id)
        return ids


def _extract_relations(record: dict) -> dict[str, Any]:
    """Extract relation-like fields from a normalized record."""
    relations = {}
    for field in RELATION_FIELDS:
        val = record.get(field)
        if val is not None:
            relations[field] = val
    return relations


def compute_diff(
    old_snapshot: dict[str, dict],
    new_snapshot: dict[str, dict],
) -> SemanticDiff:
    """Compute semantic diff between two snapshots.

    Args:
        old_snapshot: {entity_id: normalized_record_dict}
        new_snapshot: {entity_id: normalized_record_dict}

    Returns:
        SemanticDiff with all entity-level changes
    """
    diff = SemanticDiff()
    all_ids = set(old_snapshot.keys()) | set(new_snapshot.keys())

    for eid in all_ids:
        old_rec = old_snapshot.get(eid)
        new_rec = new_snapshot.get(eid)

        if old_rec is None and new_rec is not None:
            diff.entity_diffs.append(EntityDiff(entity_id=eid, added=True))
            diff.added_count += 1
            continue

        if old_rec is not None and new_rec is None:
            diff.entity_diffs.append(EntityDiff(entity_id=eid, removed=True))
            diff.removed_count += 1
            continue

        # Both exist — compare fields
        changes = []
        all_fields = set(old_rec.keys()) | set(new_rec.keys())
        for field in sorted(all_fields):
            old_val = old_rec.get(field)
            new_val = new_rec.get(field)
            if old_val != new_val:
                materiality = classify_change(field)
                changes.append(FieldChange(
                    field=field,
                    old_value=old_val,
                    new_value=new_val,
                    materiality=materiality,
                ))

        if changes:
            diff.entity_diffs.append(EntityDiff(
                entity_id=eid,
                changed_fields=changes,
            ))
            diff.changed_count += 1
            diff.material_change_count += len([c for c in changes if c.materiality != ChangeKind.COSMETIC])

    return diff
