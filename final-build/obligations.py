from __future__ import annotations

import uuid

from .model import ClaimState, ImpactReport, ProofObligation


def obligations_from_impact(report: ImpactReport) -> list[ProofObligation]:
    out: list[ProofObligation] = []
    for impact in report.claims:
        if impact.state in {ClaimState.CURRENT.value, ClaimState.VERIFIED_CURRENT.value}:
            continue
        if impact.state == ClaimState.BLOCKED.value:
            action = "RETRY_SOURCE"
        elif impact.state == ClaimState.HUMAN_REVIEW_REQUIRED.value:
            action = "HUMAN_REVIEW"
        else:
            action = "RECOMPUTE"
        out.append(ProofObligation(
            obligation_id="po:" + uuid.uuid4().hex[:14],
            analysis_id=report.analysis_id,
            claim_id=impact.claim_id,
            trigger_change_ids=impact.change_ids,
            reason="; ".join(impact.reasons) or impact.state,
            action=action,
        ))
    return out
