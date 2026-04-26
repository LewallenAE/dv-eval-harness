#!/usr/bin/env python3
"""
Primary entry point for the DV Agent Eval Harness.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import json
from pathlib import Path
from typing import Any

# ----------------- Third Party Library -----------------
from fastapi import FastAPI, HTTPException

# ----------------- Application Imports -----------------
from app.api.v1.eval import router as eval_router
from app.schemas.hardware import DVCase, Trajectory
from app.services.agent_runner import run_agent_on_case

# ----------------- Module-level Configuration -----------------
app = FastAPI(
    description="Deterministic evaluation harness for hardware-aware AI agents.",
    title="DV Agent Eval Harness",
    version="0.1.0",
)

# Robust Pathing for WSL/Linux
BACKEND_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = BACKEND_DIR / "mock_cases"
TRACES_DIR = BACKEND_DIR / "traces"
TRACE_FILE = TRACES_DIR / "eval_runs.jsonl"

TRACES_DIR.mkdir(parents=True, exist_ok=True)

# Include Routers
app.include_router(eval_router)

def load_case(case_id: str) -> DVCase:
    case_path = CASES_DIR / f"{case_id}.json"
    if not case_path.exists():
        raise HTTPException(status_code=404, detail="Case not found")
    return DVCase(**json.loads(case_path.read_text(encoding="utf-8")))

@app.get("/")
def root() -> dict[str, str]:
    return {"service": "DV Agent Eval Harness", "status": "ok"}

@app.get("/cases")
def list_cases() -> list[str]:
    return sorted(case_path.stem for case_path in CASES_DIR.glob("*.json"))

@app.post("/run-case/{case_id}", response_model=Trajectory)
def run_case(case_id: str):
    case = load_case(case_id)
    trajectory = run_agent_on_case(case)

    # Persist the trace to the local .jsonl store
    with TRACE_FILE.open("a", encoding="utf-8") as trace_handle:
        trace_handle.write(trajectory.model_dump_json() + "\n")

    return trajectory

@app.get("/traces")
def get_traces() -> list[dict[str, Any]]:
    if not TRACE_FILE.exists():
        return []
    return [
        json.loads(line)
        for line in TRACE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]