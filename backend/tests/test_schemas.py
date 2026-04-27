from __future__ import annotations

from app.schemas.design_patterns import FIFOSchema, FSMSchema, FSMStateEncoding
from app.schemas.hardware import CaseFamily, FIFOCase, FSMCase, parse_dv_case


def test_parse_dv_case_infers_fifo_family() -> None:
    case = parse_dv_case(
        {
            "bug_signature": "wr_ptr <= wr_ptr + 1",
            "description": "FIFO write pointer increments while full.",
            "expected_fix_contains": "if (!fifo_full) wr_ptr <= wr_ptr + 1",
            "expected_root_cause": "FIFO overflow write",
            "failure_log": "UVM_ERROR: overflow",
            "fix_replacement": "if (!fifo_full) wr_ptr <= wr_ptr + 1",
            "id": "fifo_overflow_bug",
            "metadata": {"category": "Buffer"},
            "rtl": "module fifo; endmodule",
            "success_log": "UVM_INFO: pass",
            "testbench": "fifo test",
            "title": "FIFO overflow",
        }
    )

    assert isinstance(case, FIFOCase)
    assert case.family == CaseFamily.FIFO_BUFFER


def test_parse_dv_case_infers_fsm_family() -> None:
    case = parse_dv_case(
        {
            "bug_signature": "state = BUSY",
            "description": "Controller state machine remains in IDLE.",
            "expected_fix_contains": "state <= BUSY",
            "expected_root_cause": "blocking assignment used in sequential FSM logic",
            "failure_log": "UVM_ERROR: stuck",
            "fix_replacement": "state <= BUSY",
            "id": "fsm_stuck_bug",
            "metadata": {"category": "FSM"},
            "rtl": "module controller; endmodule",
            "success_log": "UVM_INFO: pass",
            "testbench": "fsm test",
            "title": "FSM stuck in IDLE",
        }
    )

    assert isinstance(case, FSMCase)
    assert case.family == CaseFamily.FSM_CONTROLLER


def test_design_pattern_computed_fields() -> None:
    fifo = FIFOSchema(data_width=8, depth=16, id="fifo_16x8")
    binary_fsm = FSMSchema(id="fsm_binary", states=["IDLE", "BUSY", "DONE"])
    one_hot_fsm = FSMSchema(
        encoding_type=FSMStateEncoding.ONE_HOT,
        id="fsm_one_hot",
        states=["IDLE", "BUSY", "DONE"],
    )

    assert fifo.pointer_width == 5
    assert binary_fsm.bit_width == 2
    assert one_hot_fsm.bit_width == 3
