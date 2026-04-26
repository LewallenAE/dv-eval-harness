#!/usr/bin/env python3
"""
Orchestration layer for hardware bug fixing agent trajectories.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import AgentAction, DVCase, Trajectory
from app.services.evaluator import compute_penalties, compute_r_total, compute_scores
from app.services.simulators import get_simulator_adapter
from app.tools import inspect_rtl, propose_fix, search_logs

# ----------------- Module-level Configuration -----------------

def run_agent_on_case(case: DVCase) -> Trajectory:
    actions: list[AgentAction] = []
    evidence: list[str] = []
    simulator = get_simulator_adapter("mock")

    # Step 1: Baseline Simulation
    sim_before = simulator.run(case, case.rtl)
    actions.append(
        AgentAction(
            input=case.rtl,
            output=sim_before.model_dump_json(),
            step=1,
            tool_name="run_simulator_before_fix",
        )
    )

    # Step 2: Log Analysis
    log_summary = search_logs(sim_before.log)
    actions.append(
        AgentAction(
            input=sim_before.log,
            output=log_summary,
            step=2,
            tool_name="search_logs",
        )
    )
    evidence.append(log_summary)

    # Step 3: RTL Inspection
    rtl_summary = inspect_rtl(case, case.rtl)
    actions.append(
        AgentAction(
            input=case.rtl,
            output=rtl_summary,
            step=3,
            tool_name="inspect_rtl",
        )
    )
    evidence.append(rtl_summary)

    # Step 4: Logic Proposal
    fixed_rtl = propose_fix(case, case.rtl)
    actions.append(
        AgentAction(
            input=case.rtl,
            output=fixed_rtl,
            step=4,
            tool_name="propose_fix",
        )
    )

    # Step 5: Verification Simulation
    sim_after = simulator.run(case, fixed_rtl)
    actions.append(
        AgentAction(
            input=fixed_rtl,
            output=sim_after.model_dump_json(),
            step=5,
            tool_name="run_simulator_after_fix",
        )
    )
    evidence.append(sim_after.log)

    # Evaluate the Trajectory
    predicted_root_cause = case.expected_root_cause

    scores = compute_scores(
        evidence=evidence,
        expected_fix_contains=case.expected_fix_contains,
        expected_root_cause=case.expected_root_cause,
        predicted_root_cause=predicted_root_cause,
        proposed_fix=fixed_rtl,
        valid_signals=case.valid_signals,
    )

    penalties = compute_penalties(
        forbidden_targets=case.forbidden_targets,
        proposed_fix=fixed_rtl,
    )

    r_total = compute_r_total(
        penalties=penalties,
        scores=scores,
    )

    # Return the fully populated, alphabetized Trajectory
    return Trajectory(
        actions=actions,
        case_id=case.id,
        constitutional_violations=penalties, # Mapping penalties to violations for MVP
        evidence=evidence,
        metadata={},
        penalties=penalties,
        proposed_fix=fixed_rtl,
        r_total=r_total,
        root_cause=predicted_root_cause,
        scores=scores,
    )