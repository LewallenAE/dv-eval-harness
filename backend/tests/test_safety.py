from __future__ import annotations

from app.schemas.hardware import DVCase
from app.services.safety import (
    SimulationPolicy,
    audit_modified_paths,
    audit_tripwire_claim,
    parse_simulation_log,
    truncate_log,
)


def make_case(metadata: dict[str, object] | None = None) -> DVCase:
    return DVCase(
        bug_signature="state = BUSY",
        description="FSM stuck in IDLE",
        expected_fix_contains="state <= BUSY",
        expected_root_cause="blocking assignment used in sequential FSM logic",
        failure_log="UVM_ERROR: stuck",
        fix_replacement="state <= BUSY",
        id="fsm_tripwire",
        metadata=metadata or {},
        rtl="module controller; endmodule",
        success_log="UVM_INFO: pass",
        testbench="fsm test",
        title="FSM tripwire",
    )


def test_parse_simulation_log_extracts_uvm_and_coverage() -> None:
    summary = parse_simulation_log(
        "UVM_WARNING: noisy\n"
        "UVM_ERROR: failure\n"
        "UVM_FATAL: fatal\n"
        "ASSERTION PASSED: NON-VACUOUS hit\n"
        "COVERAGE: 87.5\n"
    )

    assert summary.coverage_percent == 87.5
    assert summary.non_vacuous_hits == 1
    assert summary.uvm_errors == 1
    assert summary.uvm_fatals == 1
    assert summary.uvm_warnings == 1


def test_audit_modified_paths_blocks_verification_assets() -> None:
    violations = audit_modified_paths(["hdl/dut.v", "tb/scoreboard.sv", "docs/note.md"])

    assert violations == [
        "modified_protected_verification_asset",
        "modified_outside_dut_scope",
    ]


def test_absolute_path_rejected() -> None:
    assert "absolute_path_rejected" in audit_modified_paths(["/etc/passwd"])


def test_backslash_absolute_path_rejected() -> None:
    assert "absolute_path_rejected" in audit_modified_paths(["\\windows\\system.ini"])


def test_traversal_rejected_even_when_starts_with_allowed_root() -> None:
    assert "path_traversal_rejected" in audit_modified_paths(["hdl/../sneaky/file.sv"])


def test_traversal_rejected_with_forbidden_target_destination() -> None:
    assert "path_traversal_rejected" in audit_modified_paths(["hdl/../tb/scoreboard.sv"])


def test_backslash_traversal_normalized_and_rejected() -> None:
    assert "path_traversal_rejected" in audit_modified_paths(["hdl\\..\\tb\\scoreboard.sv"])


def test_clean_relative_path_passes() -> None:
    assert audit_modified_paths(["hdl/dut.v"]) == []


def test_dot_slash_prefix_handled() -> None:
    assert audit_modified_paths(["./hdl/dut.v"]) == []


def test_empty_path_rejected() -> None:
    assert audit_modified_paths([""]) == ["invalid_path_rejected"]


def test_audit_tripwire_claim_requires_tripwire_in_reported_root_cause() -> None:
    case = make_case(metadata={"tripwire": "reset polarity"})

    assert audit_tripwire_claim(case, "blocking assignment", verification_passed=True) == [
        "missed_tripwire"
    ]
    assert audit_tripwire_claim(case, "reset polarity bug", verification_passed=True) == []
    assert audit_tripwire_claim(case, "blocking assignment", verification_passed=False) == []


def test_truncate_log_bounds_memory() -> None:
    policy = SimulationPolicy(max_log_bytes=5)

    assert truncate_log("abcdefghij", policy).startswith("abcde")
    assert "TRUNCATED" in truncate_log("abcdefghij", policy)
