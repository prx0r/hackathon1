from __future__ import annotations

"""Small deterministic delta engine for common research-intelligence aggregates.

This is deliberately not a reimplementation of DBSP. It demonstrates the same
incremental-view-maintenance principle for the operations Research CI currently
uses: count, sum and ratio/share.
"""

from dataclasses import dataclass, asdict
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class DeltaResult:
    old_value: Any
    new_value: Any
    inserted: int
    removed: int
    recomputed_rows: int

    def to_dict(self):
        return asdict(self)


def keyed_delta(old: Iterable[dict], new: Iterable[dict], key: Callable[[dict], str]) -> tuple[list[dict], list[dict], list[tuple[dict,dict]]]:
    a = {key(x): x for x in old}
    b = {key(x): x for x in new}
    inserted = [b[k] for k in sorted(set(b) - set(a))]
    removed = [a[k] for k in sorted(set(a) - set(b))]
    changed = [(a[k], b[k]) for k in sorted(set(a) & set(b)) if a[k] != b[k]]
    return inserted, removed, changed


def incremental_count(old_rows: list[dict], new_rows: list[dict], predicate: Callable[[dict], bool], key=lambda x: str(x.get("id"))) -> DeltaResult:
    old_value = sum(bool(predicate(x)) for x in old_rows)
    ins, rem, changed = keyed_delta(old_rows, new_rows, key)
    value = old_value
    for x in rem:
        value -= int(bool(predicate(x)))
    for x in ins:
        value += int(bool(predicate(x)))
    for before, after in changed:
        value += int(bool(predicate(after))) - int(bool(predicate(before)))
    return DeltaResult(old_value, value, len(ins), len(rem), len(ins)+len(rem)+len(changed))


def incremental_share(old_rows: list[dict], new_rows: list[dict], numerator: Callable[[dict], bool], denominator: Callable[[dict], bool], key=lambda x: str(x.get("id"))) -> dict[str, Any]:
    num = incremental_count(old_rows, new_rows, lambda x: denominator(x) and numerator(x), key)
    den = incremental_count(old_rows, new_rows, denominator, key)
    old_share = None if den.old_value == 0 else num.old_value / den.old_value
    new_share = None if den.new_value == 0 else num.new_value / den.new_value
    return {
        "old_numerator": num.old_value, "new_numerator": num.new_value,
        "old_denominator": den.old_value, "new_denominator": den.new_value,
        "old_share": old_share, "new_share": new_share,
        "recomputed_rows": max(num.recomputed_rows, den.recomputed_rows),
    }
