#!/usr/bin/env python3
"""
Deterministic reward logic for hardware-aware agentic evaluation.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import EvaluationScores

# ----------------- Module-level Configuration -----------------

def compute_penalties(forbidden_targets: list[str], proposed_fix: str) -> list[str]:
    penalties: list[str] = []
    for target in sorted(forbidden_targets):
        if target.lower() in proposed_fix.lower():
            penalties.append("modified_forbidden_target")
    return penalties

def compute_r_total(penalties: list[str], scores: EvaluationScores) -> float:
    r_total = (
        0.25 * scores.evidence_quality +
        0.15 * scores.fix_plausibility +
        0.10 * scores.no_hallucinated_signals +
        0.30 * scores.root_cause_correct +
        0.20 * scores.tool_use_correctness
    )
    for p in sorted(penalties):
        if p == "modified_forbidden_target":
            r_total -= 0.30
    return max(r_total, 0.0)

def compute_scores(
    evidence: list[str],
    expected_fix_contains: str | None,
    expected_root_cause: str,
    predicted_root_cause: str,
    proposed_fix: str,
    valid_signals: list[str],
) -> EvaluationScores:
    expected = expected_root_cause.lower().strip()
    predicted = predicted_root_cause.lower().strip()

    return EvaluationScores(
        evidence_quality=1.0 if evidence else 0.0,
        fix_plausibility=1.0 if (expected_fix_contains and expected_fix_contains in proposed_fix) 
                         else 0.8 if ("<=" in proposed_fix) else 0.5,
        no_hallucinated_signals=1.0,
        root_cause_correct=1.0 if expected in predicted else 0.0,
        tool_use_correctness=1.0 if len(evidence) >= 2 else 0.5,
    )