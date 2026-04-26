#!/usr/bin/env python3
"""
This Module houses the DPO logic for pi and ref logs calculated using sigmoid 
to create the rewards system for our agentic model.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------
import torch
import torch.nn.functional as F

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------

def compute_dpo_loss(
    beta: float = 0.1,
    pi_logps: torch.Tensor,
    ref_logps: torch.Tensor,
    yl_idxs: torch.Tensor,
    yw_idxs: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    DPO Objective: Increase the likelihood of yw relative to yl, weighted by 
    the error in the implicit reward model.

    pi_logps: Policy log probabilities, shape (B, )
    ref_logps: Reference model log probabilities, shape (B, )
    yw_idxs: Preferred completion (winner) indices, shape (T, )
    yl_idxs: Dispreferred completion (loser) indices, shape(T, )
    beta: Temperature controlling strength of KL Penalty (default 0.1)
    """
    # Extract log-probs for preferred (yw) and dispreferred (yl) fixes 
    pi_yw_logps, pi_yl_logps = pi_logps[yw_idxs], pi_logps[yl_idxs]
    ref_yw_logps, ref_yl_logps = ref_logps[yw_idxs], ref_logps[yl_idxs]

    # Calculate the log ratios between current policy and reference policy
    pi_logratios = pi_yw_logps - pi_yl_logps
    ref_logratios = ref_yw_logps - ref_yl_logps

    # DPO Objective: Optimize the model to prefer 'yw' over 'yl' 
    # based on the relative probability increase compared to the reference model.
    losses = -F.logsigmoid(beta * (pi_logratios - ref_logratios))

    # Implicit reward for logging and monitoring training stability
    rewards = beta * (pi_logps - ref_logps).detach()

    return losses, rewards