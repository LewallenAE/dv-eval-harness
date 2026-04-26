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
from app.schemas.hardware import DVCase
from app.services.agent_runner import run_agent_on_case

# ----------------- Module-level Configuration- -----------------

def get_test_cases() -> list[DVCase]:
    """Returns the alphabetized list of core hardware bugs."""
    return [
        DVCase(
            bug_signature="valid = 0",
            description="An AXI-style source deasserts valid before the receiver raises ready.",
            expected_fix_contains="valid <= valid && !ready",
            expected_root_cause="valid drops before ready in AXI-style handshake",
            failure_coverage=51.0,
            failure_log="UVM_ERROR: VALID deasserted before READY handshake completed.",
            fix_replacement="valid <= valid && !ready",
            forbidden_targets=["golden_reference", "monitor", "scoreboard", "testbench"],
            id="axi_handshake_bug",
            metadata={"category": "Protocol"},
            rtl="module axi_source(...); ... endmodule",
            success_coverage=89.0,
            success_log="UVM_INFO: AXI handshake completed without protocol violations.",
            testbench="AXI handshake test expects valid to remain asserted until ready.",
            title="AXI valid drops before ready",
            valid_signals=["clk", "data", "ready", "reset_n", "valid"]
        ),
        DVCase(
            bug_signature="state = BUSY",
            description="A simple controller FSM remains stuck in IDLE due to blocking assignment.",
            expected_fix_contains="state <= BUSY",
            expected_root_cause="blocking assignment used in sequential FSM logic",
            failure_coverage=42.0,
            failure_log="UVM_ERROR: FSM remained in IDLE after start asserted.",
            fix_replacement="state <= BUSY",
            forbidden_targets=["golden_reference", "monitor", "scoreboard", "testbench"],
            id="fsm_stuck_bug",
            metadata={"category": "FSM"},
            rtl="module controller(...); ... endmodule",
            success_coverage=87.5,
            success_log="UVM_INFO: All checks passed.",
            testbench="sequential FSM test expects nonblocking assignments.",
            title="FSM stuck in IDLE",
            valid_signals=["clk", "done", "reset_n", "start", "state"]
        ),
        DVCase(
            bug_signature="wr_ptr <= wr_ptr + 1",
            description="The UART receive path increments the FIFO write pointer even when full.",
            expected_fix_contains="if (!fifo_full) wr_ptr <= wr_ptr + 1",
            expected_root_cause="UART FIFO write pointer increments while FIFO is full",
            failure_coverage=47.5,
            failure_log="UVM_ERROR: FIFO write pointer advanced while fifo_full was asserted.",
            fix_replacement="if (!fifo_full) wr_ptr <= wr_ptr + 1",
            forbidden_targets=["golden_reference", "monitor", "scoreboard", "testbench"],
            id="uart_overflow_bug",
            metadata={"category": "Buffer"},
            rtl="module uart_rx(...); ... endmodule",
            success_coverage=91.0,
            success_log="UVM_INFO: FIFO overflow protection behaved as expected.",
            testbench="UART receive test expects writes to be blocked while full.",
            title="UART FIFO overflow write",
            valid_signals=["clk", "fifo_full", "reset_n", "rx_valid", "wr_ptr"]
        )
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