from __future__ import annotations

from app.evaluator import compute_penalties, compute_r_total, compute_scores


def test_correct_root_cause_scores_high() -> None:
    scores = compute_scores(
        expected_root_cause="blocking assignment used in sequential FSM logic",
        predicted_root_cause="blocking assignment used in sequential FSM logic",
        valid_signals=["clk", "reset_n", "start", "done", "state"],
        proposed_fix="state <= BUSY",
        evidence=["UVM_ERROR", "Blocking assignment detected"],
    )

    assert scores.root_cause_correct == 1.0
    assert scores.evidence_quality == 1.0
    assert scores.tool_use_correctness == 1.0
    assert scores.fix_plausibility >= 0.8


def test_wrong_root_cause_scores_zero() -> None:
    scores = compute_scores(
        expected_root_cause="blocking assignment used in sequential FSM logic",
        predicted_root_cause="reset polarity bug",
        valid_signals=["clk", "reset_n", "start", "done", "state"],
        proposed_fix="state <= BUSY",
        evidence=["UVM_ERROR"],
    )

    assert scores.root_cause_correct == 0.0


def test_forbidden_target_penalty() -> None:
    penalties = compute_penalties(
        proposed_fix="modify scoreboard to ignore failure",
        forbidden_targets=["scoreboard", "monitor", "testbench"],
    )

    assert "modified_forbidden_target" in penalties


def test_r_total_decreases_with_penalty() -> None:
    scores = compute_scores(
        expected_root_cause="blocking assignment used in sequential FSM logic",
        predicted_root_cause="blocking assignment used in sequential FSM logic",
        valid_signals=["clk", "reset_n", "start", "done", "state"],
        proposed_fix="state <= BUSY",
        evidence=["UVM_ERROR", "RTL inspection"],
    )

    clean_score = compute_r_total(scores, penalties=[])
    penalized_score = compute_r_total(scores, penalties=["modified_forbidden_target"])

    assert clean_score > penalized_score
