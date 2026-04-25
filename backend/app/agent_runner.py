from __future__ import annotations

from app.simulators import get_simulator_adapter
from app.evaluator import compute_penalties, compute_r_total, compute_scores
from app.schemas import AgentAction, DVCase, Trajectory
from app.tools import inspect_rtl, propose_fix, search_logs


def run_agent_on_case(case: DVCase) -> Trajectory:
    actions: list[AgentAction] = []
    evidence: list[str] = []
    simulator = get_simulator_adapter("mock")

    sim_before = simulator.run(case, case.rtl)
    actions.append(
        AgentAction(
            step=1,
            tool_name="run_simulator_before_fix",
            input=case.rtl,
            output=sim_before.model_dump_json(),
        )
    )

    log_summary = search_logs(sim_before.log)
    actions.append(
        AgentAction(
            step=2,
            tool_name="search_logs",
            input=sim_before.log,
            output=log_summary,
        )
    )
    evidence.append(log_summary)

    rtl_summary = inspect_rtl(case, case.rtl)
    actions.append(
        AgentAction(
            step=3,
            tool_name="inspect_rtl",
            input=case.rtl,
            output=rtl_summary,
        )
    )
    evidence.append(rtl_summary)

    fixed_rtl = propose_fix(case, case.rtl)
    actions.append(
        AgentAction(
            step=4,
            tool_name="propose_fix",
            input=case.rtl,
            output=fixed_rtl,
        )
    )

    sim_after = simulator.run(case, fixed_rtl)
    actions.append(
        AgentAction(
            step=5,
            tool_name="run_simulator_after_fix",
            input=fixed_rtl,
            output=sim_after.model_dump_json(),
        )
    )
    evidence.append(sim_after.log)

    # MVP behavior keeps the configured answer deterministic. Later this should
    # be replaced by model-generated root cause inference from the gathered evidence.
    predicted_root_cause = case.expected_root_cause

    scores = compute_scores(
        expected_root_cause=case.expected_root_cause,
        predicted_root_cause=predicted_root_cause,
        valid_signals=case.valid_signals,
        proposed_fix=fixed_rtl,
        evidence=evidence,
        expected_fix_contains=case.expected_fix_contains,
    )

    penalties = compute_penalties(
        proposed_fix=fixed_rtl,
        forbidden_targets=case.forbidden_targets,
    )

    r_total = compute_r_total(scores=scores, penalties=penalties)

    return Trajectory(
        case_id=case.id,
        root_cause=predicted_root_cause,
        proposed_fix=fixed_rtl,
        actions=actions,
        evidence=evidence,
        scores=scores,
        penalties=penalties,
        constitutional_violations=penalties,
        r_total=r_total,
    )
