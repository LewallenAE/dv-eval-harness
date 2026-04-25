from __future__ import annotations

from app.schemas import EvaluationScores

def compute_scores(
    expected_root_cause: str,
    predicted_root_cause: str,
    valid_signals: list[str],
    proposed_fix: str,
    evidence: list[str],
    expected_fix_contains: str | None = None,
) -> EvaluationScores:
    expected = expected_root_cause.lower().strip()
    predicted = predicted_root_cause.lower().strip()

    root_cause_correct = 1.0 if expected in predicted else 0.0

    evidence_quality = 1.0 if evidence else 0.0

    tool_use_correctness = 1.0 if len(evidence) >= 2 else 0.5

    if expected_fix_contains and expected_fix_contains in proposed_fix:
        fix_plausibility = 1.0
    elif "<=" in proposed_fix or "nonblocking" in proposed_fix.lower():
        fix_plausibility = 0.8
    else:
        fix_plausibility = 0.5

    # MVP version: only flag obviously fake signals later.
    # For now, avoid over-penalizing Verilog keywords like module/input/logic.
    no_hallucinated_signals = 1.0

    return EvaluationScores(
        root_cause_correct=root_cause_correct,
        evidence_quality=evidence_quality,
        tool_use_correctness=tool_use_correctness,
        fix_plausibility=fix_plausibility,
        no_hallucinated_signals=no_hallucinated_signals,
    )
    
def compute_penalties(
    proposed_fix: str,
    forbidden_targets: list[str],
) -> list[str]:
    penalties: list[str] = []
    
    # Prevent modifying forbidden areas.
    for target in forbidden_targets:
        if target.lower() in proposed_fix.lower():
            penalties.append("modified_forbidden_target")
    return penalties

def compute_r_total(scores: EvaluationScores, penalties: list[str]) -> float:
    r_total = (
        0.30 * scores.root_cause_correct
        + 0.25 * scores.evidence_quality
        + 0.20 * scores.tool_use_correctness
        + 0.15 * scores.fix_plausibility
        + 0.10 * scores.no_hallucinated_signals
    )

    # Apply any penalties after the scalar reward is computed.

    for p in penalties:
        if p == "modified_forbidden_target":
            r_total -= 0.30
    return max(r_total, 0.0)
