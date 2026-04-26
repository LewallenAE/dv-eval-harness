#!/usr/bin/env python3
"""
Supabase Persistence Layer for the Design Verification Data Base. (PostgreSQL)
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import os
from typing import Any

# ----------------- Third Party Library -----------------
from dotenv import load_dotenv
from supabase import create_client

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------
load_dotenv()


SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")

if not SUPABASE_URL:
    raise RuntimeError("Missing SUPABASE_URL Environment variable.")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Missing SUPABASE_SERVICE_ROLE_KEY Environment variable")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def save_eval_run(data: dict[str, Any]) -> None:
    """Persist one evaluated trajectory to Supabase."""
    supabase.table("eval_runs").insert(data).execute()

def get_eval_runs() -> list[dict[str, Any]]:
    """Return most recent eval runs first."""
    response = (
        supabase.table("eval_runs")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data