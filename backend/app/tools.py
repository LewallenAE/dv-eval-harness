from __future__ import annotations

from typing import Any

from app.schemas import DVCase


def inspect_rtl(case: DVCase, rtl: str) -> str:
    """Summarize whether the configured bug signature appears in the RTL."""

    if case.bug_signature in rtl:
        return (
            f"Case {case.id} ({case.title}): configured bug signature detected "
            f"in RTL: {case.bug_signature!r}."
        )

    return (
        f"Case {case.id} ({case.title}): no configured bug signature detected "
        f"in RTL."
    )

def search_logs(sim_log: str) -> str:
    """Extract important failure evidence from simulation logs."""
    important_lines: list[str] = []
    critical_tokens = (
        "UVM_ERROR",
        "UVM_FATAL",
        "ASSERTION FAILED",
        "ERROR",
        "FATAL",
    )

    for line in sim_log.splitlines():
        upper_line = line.upper()
        if any(token in upper_line for token in critical_tokens):
            important_lines.append(line)

    if not important_lines:
        return "No critical simulator failures found."

    return "\n".join(important_lines)

def run_mock_simulator(case: DVCase, rtl: str) -> dict[str, Any]:
    """Return deterministic case-configured simulator outputs."""

    if case.bug_signature in rtl:
        return {
            "log": case.failure_log,
            "coverage": case.failure_coverage,
            "pass_rate": 0.60,
        }

    return {
        "log": case.success_log,
        "coverage": case.success_coverage,
        "pass_rate": 0.95,
    }


def propose_fix(case: DVCase, rtl: str) -> str:
    """Apply the configured replacement if the bug signature is still present."""

    if case.bug_signature not in rtl:
        return rtl

    return rtl.replace(case.bug_signature, case.fix_replacement)
