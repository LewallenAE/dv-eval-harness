from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.agent_runner import run_agent_on_case
from app.llm import normalize_case
from app.schemas import DVCase

app = FastAPI(
    title="DV Agent Eval Harness",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://dv-eval-harness-khotskjax-anthonys-projects-8cb2840f.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BACKEND_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = BACKEND_DIR / "mock_cases"
TRACES_DIR = BACKEND_DIR / "traces"
TRACE_FILE = TRACES_DIR / "eval_runs.jsonl"

TRACES_DIR.mkdir(parents=True, exist_ok=True)


def load_case(case_id: str) -> DVCase:
    matches = [p for p in CASES_DIR.rglob(f"{case_id}.json") if not p.name.startswith("_")]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return DVCase(**json.loads(matches[0].read_text(encoding="utf-8")))


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
    return sorted(
        case_path.stem
        for case_path in CASES_DIR.rglob("*.json")
        if not case_path.name.startswith("_")  # skip staging files
    )


@app.post("/run-case/{case_id}")
def run_case(case_id: str):
    case = load_case(case_id)
    trajectory = run_agent_on_case(case)

    with TRACE_FILE.open("a", encoding="utf-8") as trace_handle:
        trace_handle.write(trajectory.model_dump_json() + "\n")

    return trajectory


@app.post("/run-case-json")
def run_case_json(case: DVCase):
    trajectory = run_agent_on_case(case)

    with TRACE_FILE.open("a", encoding="utf-8") as trace_handle:
        trace_handle.write(trajectory.model_dump_json() + "\n")

    return trajectory


@app.post("/ingest-case")
async def ingest_case(request: Request):
    """Accept any JSON case, use Claude to fill in missing fields, return normalized DVCase preview.

    Minimum required fields: id, rtl, bug_signature, expected_root_cause.
    Returns { case: DVCase, inferred_fields: [field_names_auto_filled] }.
    """
    raw: dict[str, Any] = await request.json()

    required = {"id", "rtl", "bug_signature"}
    missing_required = required - set(raw.keys())
    if missing_required:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {sorted(missing_required)}. "
                   "At minimum provide: id, rtl, bug_signature. "
                   "Omit expected_root_cause to run in Analysis mode (agent diagnoses the bug).",
        )

    normalized, inferred_fields = normalize_case(raw)
    case = DVCase(**normalized)
    return {"case": case.model_dump(), "inferred_fields": inferred_fields}


@app.get("/traces")
def get_traces() -> list[dict[str, Any]]:
    return read_traces()
