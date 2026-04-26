#!/usr/bin/env python3
"""
API Endpoints for trajectory processing and hardware evaluation.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------
from fastapi import APIRouter, HTTPException

# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase, Trajectory
from app.services.agent_runner import run_agent_on_case

# ----------------- Module-level Configuration -----------------
router = APIRouter(prefix="/eval", tags=["Evaluation"])

@router.post("/process-trajectory", response_model=Trajectory)
async def process_eval(case: DVCase):
    """
    Directly triggers the agentic loop for a specific hardware case.
    """
    try:
        # Replaced mock logic with the actual sovereign engine
        return run_agent_on_case(case)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))