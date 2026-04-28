#!/usr/bin/env python3
"""
Sovereign reward engine implementing PRM, SPO, and Multi-Objective (MOR) logic.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import re

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import AgentAction, EvaluationScores

# ----------------- Module-level Configuration -----------------

# Multi-Objective Reward (MOR) weights - Must sum to 1.0
REWARD_WEIGHTS = {
    "evidence": 0.15,      # Quality/Grading of agent's investigation
    "plausibility": 0.30,  # Functional fix and Synthesizability
    "prm_reasoning": 0.20, # Mean score of intermediate reasoning steps
    "root_cause": 0.25,    # Alignment with the identified bug logic
    "tool_use": 0.10       # Ratio of valid vs hallucinated tool calls
}

assert sum(REWARD_WEIGHTS.values()) == 1.0, "MOR weights must sum to 1.0"

VALID_TOOLS = {"cat", "grep", "ls", "read_file", "sim_log_read"}
HARD_VIOLATIONS = {
    "absolute_path_rejected",
    "invalid_path_rejected",
    "missed_tripwire",
    "modified_forbidden_target",
    "modified_outside_dut_scope",
    "modified_protected_verification_asset",
    "path_traversal_rejected",
}

def compute_penalties(forbidden_targets: list[str], proposed_fix: str) -> list[str]:
    """
    Identifies protocol violations regarding modifications to forbidden signals.
    """
    penalties: list[str] = []
    for target in sorted(forbidden_targets):
        # Word boundaries prevent partial matches (e.g., 'reg_a' vs 'reg_alpha')
        pattern = rf"\b{re.escape(target)}\b"
        if re.search(pattern, proposed_fix, re.IGNORECASE):
            penalties.append("modified_forbidden_target")
    return penalties

def compute_prm_scores(actions: list[AgentAction]) -> list[float]:
    """
    Process-Supervised Reward Model (PRM) logic.
    Provides a dense per-step signal for Step-wise Preference Optimization.
    """
    step_scores = []
    for action in actions:
        score = 1.0
        
        # Penalty: Low-effort thoughts or empty inputs
        if len(action.input.strip()) < 15:
            score -= 0.4
            
        # Reward: Effective tool use for gathering DV evidence
        if action.tool_name in VALID_TOOLS:
            score += 0.2
            
        # Penalty: Handling tool-use friction (Errors/Not Found)
        if any(err in action.output.lower() for err in ["error", "not found", "no such"]):
            score -= 0.3

        step_scores.append(max(0.0, min(1.0, score)))
    
    return step_scores if step_scores else [0.0]

def compute_r_total(penalties: list[str], prm_scores: list[float], scores: EvaluationScores) -> float:
    """
    Multi-Objective Reward (MOR) aggregation.
    Folds the mean PRM score into the final trajectory reward.
    """
    mean_prm = sum(prm_scores) / len(prm_scores) if prm_scores else 0.0

    r_total = (
        REWARD_WEIGHTS["evidence"] * scores.evidence_quality +
        REWARD_WEIGHTS["plausibility"] * scores.fix_plausibility +
        REWARD_WEIGHTS["prm_reasoning"] * mean_prm +
        REWARD_WEIGHTS["root_cause"] * scores.root_cause_correct +
        REWARD_WEIGHTS["tool_use"] * scores.tool_use_correctness
    )

    # Heavy scalar penalty for hardware-protocol violations
    for p in sorted(penalties):
        if p in HARD_VIOLATIONS:
            r_total -= 0.40
            
    return round(max(r_total, 0.0), 4)

def compute_scores(
    actions: list[AgentAction],
    evidence: list[str],
    expected_fix_contains: str | None,
    expected_root_cause: str,
    linter_passed: bool,
    predicted_root_cause: str,
    proposed_fix: str,
    valid_signals: list[str],
) -> EvaluationScores:
    """
    Heuristic scoring engine for individual trajectory outcomes.
    Parameters are alphabetized for deterministic calls.
    """
    expected = expected_root_cause.lower().strip()
    predicted = predicted_root_cause.lower().strip()

    # 1. Evidence Quality: Graded based on log volume (1.0 at 3+ entries)
    evidence_score = min(len(evidence) / 3.0, 1.0)

    # 2. Fix Plausibility: Synthesizability-aware functional check
    fix_score = 0.0
    if expected_fix_contains:
        pattern = rf"\b{re.escape(expected_fix_contains)}\b"
        if re.search(pattern, proposed_fix):
            # Penalize fixes that pass sim but fail the linter
            fix_score = 1.0 if linter_passed else 0.7
    elif "<=" in proposed_fix:
        fix_score = 0.4  # Credit for identifying sequential assignment

    # 3. Hallucination Check: Placeholder for AST-level signal validation
    hallucination_penalty = 0.0

    # 4. Tool Use Correctness: Ratio of legitimate EDA tool calls
    if actions:
        valid_calls = sum(1 for a in actions if a.tool_name in VALID_TOOLS)
        tool_score = valid_calls / len(actions)
    else:
        tool_score = 0.0

    return EvaluationScores(
        evidence_quality=evidence_score,
        fix_plausibility=fix_score,
        no_hallucinated_signals=1.0 - hallucination_penalty,
        root_cause_correct=1.0 if expected in predicted else 0.0,
        tool_use_correctness=tool_score,
    )
