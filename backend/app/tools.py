from __future__ import annotations

from typing import Any

from app.schemas import DVCase


def _bug_present(case: DVCase, rtl: str) -> bool:
    """Return True if the bug is still present in `rtl`.

    Detection priority:
    1. expected_fix_contains — if the fix token appears in rtl the bug is gone.
    2. fix_replacement       — if the full fixed snippet is present the bug is gone.
    3. RTL identity          — if rtl matches the original buggy RTL the bug is present.
    4. bug_signature as RTL substring — legacy path for the original three cases where
       the signature was literally embedded in the RTL text.
    """
    # Fix already applied
    if case.expected_fix_contains and case.expected_fix_contains in rtl:
        return False
    if case.fix_replacement and case.fix_replacement.strip() in rtl:
        return False

    # RTL is unchanged from the original buggy version → bug still present
    if case.rtl and rtl.strip() == case.rtl.strip():
        return True

    # Legacy: bug_signature was an RTL substring (original three demo cases)
    if case.bug_signature and case.bug_signature in rtl:
        return True

    return False


def run_mock_simulator(case: DVCase, rtl: str) -> dict[str, Any]:
    """Return deterministic case-configured simulator outputs."""
    if _bug_present(case, rtl):
        return {
            "log": case.failure_log or case.bug_signature,
            "coverage": case.failure_coverage,
            "pass_rate": 0.60,
        }

    return {
        "log": case.success_log or f"All assertions passed for {case.id}.",
        "coverage": case.success_coverage,
        "pass_rate": 0.95,
    }


def inspect_rtl(case: DVCase, rtl: str) -> str:
    """Report whether the bug is detected in the RTL and what the signature indicates."""
    if _bug_present(case, rtl):
        return (
            f"Case {case.id} ({case.title}): bug detected. "
            f"Expected failure signature: {case.bug_signature!r}. "
            f"Current RTL has not yet received the fix (fix must contain: "
            f"{case.expected_fix_contains!r})."
        )

    return (
        f"Case {case.id} ({case.title}): fix verified. "
        f"RTL now contains the required correction "
        f"({case.expected_fix_contains!r} present)."
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
        if any(token in line.upper() for token in critical_tokens):
            important_lines.append(line)

    if not important_lines:
        return "No critical simulator failures found."

    return "\n".join(important_lines)


def propose_fix(case: DVCase, rtl: str) -> str:
    """Return the configured fix when the bug is still present; return rtl unchanged if already fixed."""
    if not _bug_present(case, rtl):
        return rtl

    return case.fix_replacement
