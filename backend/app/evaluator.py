from __future__ import annotations

from app.schemas import EvaluationScores

def compute_scores(
    expected_root_cause: str,
    predicted_root_cause: str,
    valid_signals: list[str],
    proposed_fix: str,
    evidence: list[str],
    expected_fix_contains: str | None = None,
    root_cause_score: float | None = None,
    sim_fix_passed: bool = False,
) -> EvaluationScores:
    """Score an agent's debug output across the five evaluation dimensions.

    When expected_root_cause is empty the case is running in Analysis mode:
    root_cause_correct is set to None and excluded from r_total weighting.
    """
    if not expected_root_cause.strip():
        # Analysis mode — no ground truth to compare against
        root_cause_correct = None
    elif root_cause_score is not None:
        root_cause_correct = root_cause_score
    else:
        expected = expected_root_cause.lower().strip()
        predicted = predicted_root_cause.lower().strip()
        root_cause_correct = 1.0 if expected in predicted else 0.0

    evidence_quality = 1.0 if evidence else 0.0

    tool_use_correctness = 1.0 if len(evidence) >= 2 else 0.5

    if expected_fix_contains and expected_fix_contains in proposed_fix:
        # Exact token match — highest confidence
        fix_plausibility = 1.0
    elif sim_fix_passed:
        # Post-fix simulation passed even without exact token — fix is functionally correct
        fix_plausibility = 0.9
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
    """Return a list of penalty labels for any forbidden targets touched by the proposed fix."""
    penalties: list[str] = []
    
    # Prevent modifying forbidden areas.
    for target in forbidden_targets:
        if target.lower() in proposed_fix.lower():
            penalties.append("modified_forbidden_target")
    return penalties

def compute_r_total(scores: EvaluationScores, penalties: list[str]) -> float:
    """Compute the scalar reward from the weighted score components minus any penalties; clamped to 0.0.

    In Analysis mode (root_cause_correct is None) the 0.30 weight is redistributed
    proportionally across the remaining four dimensions so r_total stays on [0, 1].
    """
    if scores.root_cause_correct is not None:
        r_total = (
            0.30 * scores.root_cause_correct
            + 0.25 * scores.evidence_quality
            + 0.20 * scores.tool_use_correctness
            + 0.15 * scores.fix_plausibility
            + 0.10 * scores.no_hallucinated_signals
        )
    else:
        # Redistribute the 0.30 root-cause weight across the other four (total stays 1.0)
        r_total = (
            0.36 * scores.evidence_quality
            + 0.29 * scores.tool_use_correctness
            + 0.21 * scores.fix_plausibility
            + 0.14 * scores.no_hallucinated_signals
        )

    for p in penalties:
        if p == "modified_forbidden_target":
            r_total -= 0.30
    return max(r_total, 0.0)
