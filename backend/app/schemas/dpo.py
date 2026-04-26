#!/usr/bin/env python3
"""
Data contracts for Direct Preference Optimization (DPO) batching.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------


# ----------------- Third Party Library -----------------
from pydantic import BaseModel

# ----------------- Application Imports -----------------
from app.schemas.hardware import Trajectory

# ----------------- Module-level Configuration -----------------

class DPOBatch(BaseModel):
    beta: float = 0.1
    pairs: list[DPOPair]

class DPOPair(BaseModel):
    case_id: str
    loser: Trajectory
    margin: float
    prompt: str
    winner: Trajectory