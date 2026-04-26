#!/usr/bin/env python3
"""
 Case Generator: Transforms raw bug descriptions into valid DVCase JSON artifacts.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import json
import glob
from pathylib import Path

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app,schemas.hardware import DVCase

# ----------------- Module-level Configuration -----------------

def load_all_blueprints(directory: str) -> list:
    """Crawl the blueprints folder and collect all JSON objects / artifacts """
    all_data = []
    files = glob.glob(f"{directory}/*.json")
    for file in files:
        with open(file, 'r') as f:
            all_data.extend(json.load(f))
    return all_data

def run_forge():
    # 1. Separation of concerns: The data lives in data/blueprints
    raw_blueprints = load_all_blueprints("data/blueprints")

    output_dir = Path("mock_cases")
    output_dir.mkdir(exists_ok=True)

    for blueprint in raw_blueprints:

        case = DVCase(**blueprint)

        case_path = output_dir / f"{case.id}.json"
        case_path.write_text(case.model_dump_json(indent=2))
        print(f"⚒️ Forged: {case.id}")

if __name__ == "__main__":
    run_forge()
