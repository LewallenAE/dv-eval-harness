from __future__ import annotations

from app.storage import _to_eval_run_row


def test_to_eval_run_row_matches_supabase_columns() -> None:
    row = _to_eval_run_row(
        {
            "actions": [{"step": 1}],
            "case_id": "fsm_stuck_bug",
            "constitutional_violations": [],
            "evidence": ["UVM_ERROR"],
            "metadata": {"simulator": "mock"},
            "penalties": [],
            "proposed_fix": "state <= BUSY;",
            "r_total": 0.99,
            "root_cause": "blocking assignment",
            "scores": {"root_cause_correct": 1.0},
        }
    )

    assert list(row) == [
        "actions",
        "case_id",
        "constitutional_violations",
        "evidence",
        "metadata",
        "penalties",
        "proposed_fix",
        "r_total",
        "root_cause",
        "scores",
    ]
    assert row["case_id"] == "fsm_stuck_bug"
    assert row["r_total"] == 0.99
