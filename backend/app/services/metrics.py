#!/usr/bin/env python3
"""
Evaluation metrics beyond the primary reward signal.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import math

# ----------------- Third Party Library -----------------

# ----------------- Application Imports -----------------
from app.schemas.hardware import EvaluationScores

# ----------------- Module-level Configuration -----------------


def compute_r2_holdout_score(
    penalties: list[str],
    scores: EvaluationScores,
) -> float:
    """
    Independent conservative reward used as R2 telemetry.

    R2 intentionally excludes PRM/tool-use credit so threshold hugging in R1 is
    visible as a gap between process-heavy and outcome-heavy scoring.
    """
    hard_penalty = 0.25 * len(penalties)
    score = (
        0.35 * scores.root_cause_correct
        + 0.35 * scores.fix_plausibility
        + 0.20 * scores.evidence_quality
        + 0.10 * scores.no_hallucinated_signals
        - hard_penalty
    )
    return round(max(0.0, min(1.0, score)), 4)


def estimate_pass_at_k(total: int, correct: int, k: int) -> float:
    """Unbiased pass@k estimator from Codex-style evaluation."""
    if total <= 0 or correct <= 0 or k <= 0:
        return 0.0
    if total - correct < k:
        return 1.0
    return round(1.0 - math.comb(total - correct, k) / math.comb(total, k), 4)
