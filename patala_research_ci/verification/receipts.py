"""EvidenceReceipt — proof-carrying verification results.

Adapted from QDW VerificationService: a receipt binds a verification run
to its inputs, plan, execution environment, and outputs. It can be verified
later without rerunning the checks.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    """Result of a single verification check."""
    check_id: str
    status: str  # PASS, FAIL, SKIP, ERROR
    stdout_hash: str = ""
    stderr_hash: str = ""
    duration_ms: int = 0
    note: str = ""

    def to_dict(self) -> dict:
        d = {
            "check_id": self.check_id,
            "status": self.status,
        }
        if self.stdout_hash: d["stdout_hash"] = self.stdout_hash
        if self.stderr_hash: d["stderr_hash"] = self.stderr_hash
        if self.duration_ms: d["duration_ms"] = self.duration_ms
        if self.note: d["note"] = self.note
        return d


@dataclass
class EvidenceReceipt:
    """A proof-carrying receipt for a verification run.

    This is the "Trust Receipt" — machine-verifiable evidence that a
    claim was checked against specific inputs with a specific plan.
    """
    receipt_id: str
    claim_id: str
    obligation_id: str

    # What was checked
    inputs: dict = field(default_factory=dict)  # snapshot digests, query hashes
    plan_hash: str = ""
    analysis_id: str = ""

    # How it was checked
    environment: dict = field(default_factory=dict)  # platform, python version
    checks: list[CheckResult] = field(default_factory=list)

    # What was produced
    artifacts: list[dict] = field(default_factory=list)  # {path, sha256, size}

    # Final verdict
    status: str = ""  # PROVED_CURRENT, STILL_STALE, FAILED, INCONCLUSIVE
    receipt_hash: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not self.receipt_hash:
            self.receipt_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Hash the receipt contents for integrity."""
        contents = {
            "receipt_id": self.receipt_id,
            "claim_id": self.claim_id,
            "obligation_id": self.obligation_id,
            "inputs": self.inputs,
            "plan_hash": self.plan_hash,
            "checks": [c.to_dict() for c in self.checks],
            "status": self.status,
        }
        canonical = json.dumps(contents, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "receipt_id": self.receipt_id,
            "claim_id": self.claim_id,
            "obligation_id": self.obligation_id,
            "inputs": self.inputs,
            "plan_hash": self.plan_hash,
            "analysis_id": self.analysis_id,
            "environment": self.environment,
            "checks": [c.to_dict() for c in self.checks],
            "artifacts": self.artifacts,
            "status": self.status,
            "receipt_hash": self.receipt_hash,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> EvidenceReceipt:
        return cls(
            receipt_id=d["receipt_id"],
            claim_id=d["claim_id"],
            obligation_id=d["obligation_id"],
            inputs=d.get("inputs", {}),
            plan_hash=d.get("plan_hash", ""),
            analysis_id=d.get("analysis_id", ""),
            environment=d.get("environment", {}),
            checks=[CheckResult(**c) for c in d.get("checks", [])],
            artifacts=d.get("artifacts", []),
            status=d.get("status", ""),
            receipt_hash=d.get("receipt_hash", ""),
            created_at=d.get("created_at", ""),
        )

    def verify_integrity(self) -> bool:
        """Verify the receipt hash is correct."""
        return self.receipt_hash == self._compute_hash()

    @property
    def all_passed(self) -> bool:
        return all(c.status == "PASS" for c in self.checks)
