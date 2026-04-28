from __future__ import annotations

from app.schemas.hardware import EvaluationScores
from app.services.metrics import compute_r2_holdout_score, estimate_pass_at_k


def test_compute_r2_holdout_score_penalizes_violations() -> None:
    scores = EvaluationScores(
        evidence_quality=1.0,
        fix_plausibility=1.0,
        no_hallucinated_signals=1.0,
        root_cause_correct=1.0,
        tool_use_correctness=1.0,
    )

    assert compute_r2_holdout_score([], scores) == 1.0
    assert compute_r2_holdout_score(["missed_tripwire"], scores) == 0.75


def test_estimate_pass_at_k() -> None:
    assert estimate_pass_at_k(total=10, correct=0, k=1) == 0.0
    assert estimate_pass_at_k(total=10, correct=3, k=1) == 0.3
    assert estimate_pass_at_k(total=10, correct=3, k=5) == 0.9167
    assert estimate_pass_at_k(total=3, correct=1, k=3) == 1.0
