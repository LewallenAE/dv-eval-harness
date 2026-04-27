#!/usr/bin/env python3
"""
Persistence layer for evaluated trajectory runs.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import json
import os
from pathlib import Path
from typing import Any

# ----------------- Third Party Library -----------------
from dotenv import load_dotenv
from supabase import Client, create_client

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------
load_dotenv()


BACKEND_DIR = Path(__file__).resolve().parents[1]
LOCAL_STORE = BACKEND_DIR / "eval_runs.jsonl"

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")


supabase: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def _read_local_runs() -> list[dict[str, Any]]:
    """Read locally persisted eval runs, newest first."""
    if not LOCAL_STORE.exists():
        return []

    runs: list[dict[str, Any]] = []
    for line in LOCAL_STORE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            runs.append(json.loads(line))
    return list(reversed(runs))


def save_eval_run(data: dict[str, Any]) -> None:
    """Persist one evaluated trajectory."""
    if supabase is not None:
        try:
            supabase.table("eval_runs").insert(data).execute()
            return
        except Exception:
            # Local evaluation must remain usable if the remote schema is stale.
            pass

    with LOCAL_STORE.open("a", encoding="utf-8") as store:
        store.write(json.dumps(data, sort_keys=True) + "\n")

def get_eval_runs() -> list[dict[str, Any]]:
    """Return most recent eval runs first."""
    if supabase is None:
        return _read_local_runs()

    try:
        response = (
            supabase.table("eval_runs")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )
        return response.data
    except Exception:
        return _read_local_runs()
