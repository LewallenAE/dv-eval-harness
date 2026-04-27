#!/usr/bin/env python3
"""
Sovereign Smoke Test: Verifying the full hardware-aware agentic loop 
across AXI, FSM, and UART failure modes.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import json
from pathlib import Path

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase, parse_dv_case
from app.services.agent_runner import run_agent_on_case

# ----------------- Module-level Configuration- -----------------

def get_test_cases() -> list[DVCase]:
    """Returns the alphabetized list of core hardware bugs."""
    cases_dir = Path(__file__).resolve().parent / "mock_cases"
    return [
        parse_dv_case(json.loads(case_path.read_text(encoding="utf-8")))
        for case_path in sorted(cases_dir.glob("*.json"))
    ]

def main():
    print("🚀 [START] Launching Sovereign Verification Suite...")
    
    cases = get_test_cases()
    results = []

    for case in cases:
        print(f"\nProcessing: {case.title} ({case.id})...")
        try:
            # Execute the loop
            trajectory = run_agent_on_case(case)
            
            # Print TADA Metrics
            print(f"  | R_Total:  {trajectory.r_total:.2f}")
            print(f"  | Correct:  {trajectory.scores.root_cause_correct == 1.0}")
            print(f"  | Evidence: {len(trajectory.evidence)} items")
            
            results.append(trajectory)

        except Exception as e:
            print(f"  | ❌ ERROR: {str(e)}")

    # Persistence Check
    output_path = Path("smoke_test_results.json")
    with output_path.open("w", encoding="utf-8") as f:
        # Pydantic dump of the list of trajectories
        json_data = [t.model_dump() for t in results]
        json.dump(json_data, f, indent=2)

    print(f"\n✅ HURRAY! Suite complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
