#!/usr/bin/env python3
"""
 Case Generator: Transforms raw bug descriptions into valid DVCase JSON artifacts.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import glob
import json
from pathlib import Path

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import parse_dv_case

# ----------------- Module-level Configuration -----------------

def load_all_blueprints(directory: str) -> list:
    """Crawl the blueprints folder and collect all JSON objects / artifacts """
    all_data = []
    files = glob.glob(f"{directory}/*.json")
    for file in files:
        if Path(file).stat().st_size == 0:
            continue
        with open(file, "r", encoding="utf-8") as f:
            all_data.extend(json.load(f))
    return all_data

def run_forge() -> None:
    # 1. Separation of concerns: The data lives in data/blueprints
    raw_blueprints = load_all_blueprints("data/blueprints")

    output_dir = Path("mock_cases")
    output_dir.mkdir(exists_ok=True)

    for blueprint in raw_blueprints:

        case = parse_dv_case(blueprint)

        case_path = output_dir / f"{case.id}.json"
        case_path.write_text(case.model_dump_json(indent=2))
        print(f"⚒️ Forged: {case.id}")

if __name__ == "__main__":
    run_forge()
