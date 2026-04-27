from __future__ import annotations

import pytest

from app.services.evaluator import (
    REWARD_WEIGHTS,
    compute_penalties,
    compute_prm_scores,
    compute_r_total,
    compute_scores,
)
from app.schemas.hardware import AgentAction, EvaluationScores


def test_reward_weights_sum_to_one() -> None:
    """Invariant: MOR weights must sum to exactly 1.0 or R_total is malformed."""
    assert sum(REWARD_WEIGHTS.values()) == 1.0


def test_penalty_uses_word_boundary_not_substring() -> None:
    """Regression: 'reg_a' must not match 'reg_alpha' in proposed fix."""
    forbidden = ["reg_a"]
    fix_with_alpha = "always_ff @(posedge clk) reg_alpha <= 1'b0;"
    fix_with_target = "always_ff @(posedge clk) reg_a <= 1'b0;"

    assert compute_penalties(forbidden, fix_with_alpha) == []
    assert compute_penalties(forbidden, fix_with_target) == ["modified_forbidden_target"]


def test_prm_stacks_penalties_and_rewards() -> None:
    """A step that is low-effort, uses a valid tool, and has an error
    output stacks all three signals: 1.0 - 0.4 + 0.2 - 0.3 = 0.5."""
    action = AgentAction(
        input="too short",  # < 15 chars -> -0.4
        tool_name="grep",   # in VALID_TOOLS -> +0.2
        output="grep: error: file not found",  # -> -0.3
        step=1,
    )

    scores = compute_prm_scores([action])
    assert scores == [0.5]


def test_r_total_clamps_at_zero() -> None:
    """A perfect-but-violating trajectory must not produce negative reward."""
    perfect_scores = EvaluationScores(
        evidence_quality=1.0,
        fix_plausibility=1.0,
        no_hallucinated_signals=1.0,
        root_cause_correct=1.0,
        tool_use_correctness=1.0,
    )
    # Three violations: 1.0 - 0.40 - 0.40 - 0.40 = -0.20 -> clamps to 0.0
    penalties = ["modified_forbidden_target"] * 3
    prm = [1.0]
    assert compute_r_total(penalties, prm, perfect_scores) == 0.0


def test_tool_use_correctness_is_validity_ratio_not_volume() -> None:
    """Three actions, one valid tool -> tool_use should be 1/3, not 1.0.
    Catches the v1 bug where tool_use was secretly measuring evidence count."""
    actions = [
        AgentAction(step=1,input="checking the log carefully now", tool_name="grep", output="match found"),
        AgentAction(step=2, input="trying a fake tool here please", tool_name="magic_solve", output="ok"),
        AgentAction(step=3, input="another fake invocation here", tool_name="auto_fix", output="ok"),
    ]
    scores = compute_scores(
        actions=actions,
        evidence=["log line 1", "log line 2"],
        expected_fix_contains=None,
        expected_root_cause="fsm stuck",
        linter_passed=True,
        predicted_root_cause="fsm stuck in idle",
        proposed_fix="state <= IDLE;",
        valid_signals=["state", "clk"],
    )
    assert scores.tool_use_correctness == pytest.approx(1 / 3)
