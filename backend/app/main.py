from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from app.agent_runner import run_agent_on_case
from app.schemas import DVCase

app = FastAPI(
    title="DV Agent Eval Harness",
    version="0.1.0",
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = BACKEND_DIR / "mock_cases"
TRACES_DIR = BACKEND_DIR / "traces"
TRACE_FILE = TRACES_DIR / "eval_runs.jsonl"

TRACES_DIR.mkdir(parents=True, exist_ok=True)


def load_case(case_id: str) -> DVCase:
    case_path = CASES_DIR / f"{case_id}.json"

    if not case_path.exists():
        raise HTTPException(status_code=404, detail="Case not found")

    return DVCase(**json.loads(case_path.read_text(encoding="utf-8")))


def read_traces() -> list[dict[str, Any]]:
    if not TRACE_FILE.exists():
        return []

    return [
        json.loads(line)
        for line in TRACE_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "DV Agent Eval Harness"}


@app.get("/cases")
def list_cases() -> list[str]:
    return sorted(case_path.stem for case_path in CASES_DIR.glob("*.json"))


@app.post("/run-case/{case_id}")
def run_case(case_id: str):
    case = load_case(case_id)
    trajectory = run_agent_on_case(case)

    with TRACE_FILE.open("a", encoding="utf-8") as trace_handle:
        trace_handle.write(trajectory.model_dump_json() + "\n")

    return trajectory


@app.get("/traces")
def get_traces() -> list[dict[str, Any]]:
    return read_traces()
