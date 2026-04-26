#!/usr/bin/env python3
"""
Diagnostic and execution tools for RTL analysis, log processing, 
and hardware simulation.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
from typing import Any

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase

# ----------------- Module-level Configuration -----------------

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


def propose_fix(case: DVCase, rtl: str) -> str:
    """Apply the configured replacement if the bug signature is still present."""
    if case.bug_signature not in rtl:
        return rtl

    return rtl.replace(case.bug_signature, case.fix_replacement)


def run_mock_simulator(case: DVCase, rtl: str) -> dict[str, Any]:
    """Return deterministic case-configured simulator outputs."""
    if case.bug_signature in rtl:
        return {
            "coverage": case.failure_coverage,
            "log": case.failure_log,
            "pass_rate": 0.60,
        }

    return {
        "coverage": case.success_coverage,
        "log": case.success_log,
        "pass_rate": 0.95,
    }


def search_logs(sim_log: str) -> str:
    """Extract important failure evidence from simulation logs."""
    critical_tokens = (
        "ASSERTION FAILED",
        "ERROR",
        "FATAL",
        "UVM_ERROR",
        "UVM_FATAL",
    )
    important_lines: list[str] = []

    for line in sim_log.splitlines():
        upper_line = line.upper()
        if any(token in upper_line for token in critical_tokens):
            important_lines.append(line)

    if not important_lines:
        return "No critical simulator failures found."

    return "\n".join(important_lines)