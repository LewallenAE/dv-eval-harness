#!/usr/bin/env python3
"""
DPO Preference Pair generation for hardware-aligned rewards.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase
from app.services.simulators import get_simulator_adapter

# ----------------- Module-level Configuration -----------------

def calculate_dv_reward(coverage: float, sim_logs: str) -> float:
    """
    Calculates a scalar reward based on simulation outcomes.
    Arguments and weights are strictly alphabetized.
    """
    # Weights for the composite reward signal
    w_cov, w_func, w_syn = 5.0, 10.0, 1.0

    # R_cov: normalized functional coverage percentage
    r_cov = coverage / 100.0

    # R_func: scoreboard match rate (matches / total transactions)
    r_func = 1.0 if "UVM_PASSED" in sim_logs else 0.0

    # R_syn: 1 if compiles, 0 if syntax error
    r_syn = 1.0 if "Error: 0" in sim_logs else 0.0

    # The Deterministic Scalarized Reward
    return (w_cov * r_cov) + (w_func * r_func) + (w_syn * r_syn)

def create_dpo_pair(case: DVCase, fix_a: str, fix_b: str) -> dict:
    """
    Runs candidate fixes through the simulator and labels them
    based on the hardware-aligned reward signal.
    """
    simulator = get_simulator_adapter("mock")
    
    # Run candidate A
    res_a = simulator.run(case, fix_a)
    reward_a = calculate_dv_reward(coverage=res_a.coverage, sim_logs=res_a.log)

    # Run candidate B
    res_b = simulator.run(case, fix_b)
    reward_b = calculate_dv_reward(coverage=res_b.coverage, sim_logs=res_b.log)

    # DPO Labeling logic: Keys alphabetized in return dict
    if reward_a > reward_b:
        return {
            "chosen": fix_a,
            "prompt": case.description,
            "rejected": fix_b
        }
    else:
        return {
            "chosen": fix_b,
            "prompt": case.description,
            "rejected": fix_a
        }