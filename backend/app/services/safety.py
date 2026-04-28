#!/usr/bin/env python3
"""
Safety and audit helpers for production-oriented DV execution.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import os
from pathlib import Path, PurePosixPath
import re

# ----------------- Third Party Library -----------------
from pydantic import BaseModel, Field

# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase

# ----------------- Module-level Configuration -----------------


class LogSummary(BaseModel):
    """Structured simulator-log evidence used by the reward and audit layers."""

    coverage_percent: float | None = None
    non_vacuous_hits: int = 0
    uvm_errors: int = 0
    uvm_fatals: int = 0
    uvm_warnings: int = 0


class SimulationPolicy(BaseModel):
    """Execution policy for simulator isolation and reward-hacking guardrails."""

    allowed_write_roots: tuple[str, ...] = ("hdl/", "dut.v", "design.sv")
    forbidden_path_tokens: tuple[str, ...] = (
        "golden",
        "monitor",
        "scoreboard",
        "tb",
        "testbench",
    )
    max_log_bytes: int = Field(500_000, gt=0)
    memory_limit_mb: int = Field(512, gt=0)
    require_tripwire_detection: bool = True
    timeout_seconds: float = Field(10.0, gt=0.0)


DEFAULT_SIMULATION_POLICY = SimulationPolicy()


def audit_modified_paths(
    modified_paths: list[str],
    policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
) -> list[str]:
    """Reject edits outside DUT-owned paths or inside protected verification assets."""
    violations: list[str] = []
    allowed_roots = tuple(root.rstrip("/") for root in policy.allowed_write_roots)

    for raw_path in modified_paths:
        if Path(raw_path).is_absolute() or raw_path.startswith(("/", "\\")):
            violations.append("absolute_path_rejected")
            continue

        normalized_input = raw_path.replace("\\", "/")
        raw_parts = PurePosixPath(normalized_input).parts
        if ".." in raw_parts:
            violations.append("path_traversal_rejected")
            continue

        if normalized_input.startswith("./"):
            normalized_input = normalized_input[2:]

        normalized = PurePosixPath(normalized_input).as_posix()
        if not normalized or normalized in (".", "/"):
            violations.append("invalid_path_rejected")
            continue

        parts = tuple(part.lower() for part in PurePosixPath(normalized).parts)
        lower_path = normalized.lower()

        if any(token in parts or token in lower_path for token in policy.forbidden_path_tokens):
            violations.append("modified_protected_verification_asset")
            continue

        if not any(normalized == root or normalized.startswith(f"{root}/") for root in allowed_roots):
            violations.append("modified_outside_dut_scope")

    return violations


def audit_tripwire_claim(
    case: DVCase,
    reported_root_cause: str,
    verification_passed: bool,
    policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
) -> list[str]:
    """Flag a trajectory that claims success while missing an intentional tripwire."""
    if not policy.require_tripwire_detection:
        return []

    tripwire = str(case.metadata.get("tripwire", "")).strip().lower()
    if not tripwire:
        return []

    reported = reported_root_cause.lower()
    if verification_passed and tripwire not in reported:
        return ["missed_tripwire"]
    return []


def parse_simulation_log(log: str) -> LogSummary:
    """Extract UVM counts, coverage, and non-vacuous assertion evidence."""
    coverage_matches = re.findall(r"\bCOVERAGE:\s*([0-9]+(?:\.[0-9]+)?)", log, re.IGNORECASE)
    non_vacuous_matches = re.findall(
        r"\b(?:NON[-_ ]VACUOUS|ANTECEDENT\s+HIT)\b", log, re.IGNORECASE
    )

    return LogSummary(
        coverage_percent=float(coverage_matches[-1]) if coverage_matches else None,
        non_vacuous_hits=len(non_vacuous_matches),
        uvm_errors=len(re.findall(r"\bUVM_ERROR\b", log)),
        uvm_fatals=len(re.findall(r"\bUVM_FATAL\b", log)),
        uvm_warnings=len(re.findall(r"\bUVM_WARNING\b", log)),
    )


def truncate_log(log: str, policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY) -> str:
    """Bound retained simulator output before it enters trajectory memory."""
    encoded = log.encode("utf-8")
    if len(encoded) <= policy.max_log_bytes:
        return log

    truncated = encoded[: policy.max_log_bytes].decode("utf-8", errors="ignore")
    return f"{truncated}\n[TRUNCATED simulator log at {policy.max_log_bytes} bytes]"


def apply_process_memory_limit(policy: SimulationPolicy) -> None:
    """Apply a per-process address-space limit on platforms that expose resource."""
    try:
        import resource
    except ImportError:
        return

    limit_bytes = policy.memory_limit_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))


def supports_process_limits() -> bool:
    """Return whether subprocess memory limits can be installed on this OS."""
    return os.name == "posix"
