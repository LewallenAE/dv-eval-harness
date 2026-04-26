#!/usr/bin/env python3
"""
Orchestration layer for hardware bug fixing agent trajectories.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import asyncio
import os
import shutil
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

# ----------------- Third Party Library -----------------


# ----------------- Application Imports -----------------
from app.schemas.hardware import AgentAction, DVCase, EvaluationScores, Trajectory
from app.storage import save_eval_run

# ----------------- Module-level Configuration -----------------


class AgentRunner:
    """
    Orchestrates the Active Struggle between the Agent's proposal and the Simulator.
    """

    def __init__(self, workspace_root: str = "/tmp/dv_eval_workspace"):
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def _prepare_workspace(self, work_dir: Path, case: DVCase, proposed_fix: str) -> None:
        """
        Alphabetical helper to map the DVCase blueprints to the physical workspace.
        """
        # 1. HDL Directory setup
        hdl_dir = work_dir / "hdl"
        hdl_dir.mkdir(parents=True)
        # Fix: Write the proposed fix to the DUT, not the testbench
        (hdl_dir / "dut.v").write_text(proposed_fix)

        # 2. Testbench setup
        (work_dir / "tb.sv").write_text(case.testbench)

        # 3. Makefile setup (Dynamic Template)
        top_module = case.metadata.get("top_module", "dut")
        makefile_content = f"""
SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/hdl/dut.v
TOPLEVEL = {top_module}
MODULE = tb
include $(shell cocotb-config --makefiles)/Makefile.sim
        """
        (work_dir / "Makefile").write_text(makefile_content.strip())

    async def run_evaluation(self, case: DVCase, proposed_fix: str) -> Trajectory:
        """
        Alphabetical Orchestration of the simulation and scoring pipeline.
        """
        # Run Setup - Using Python 3.12 UTC best practice
        run_id = f"{case.id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        work_dir = self.workspace_root / run_id
        work_dir.mkdir(parents=True)

        try:
            # 1. Physical setup
            self._prepare_workspace(work_dir, case, proposed_fix)

            # 2. Execute (Icarus Verilog + Cocotb)
            process = await asyncio.create_subprocess_exec(
                "make",
                "-C", str(work_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "SIM": "icarus"}
            )
            stdout, stderr = await process.communicate()

            full_log = stdout.decode() + stderr.decode()
            success = process.returncode == 0

            # 3. Scoring (Alignment with EvaluationScores schema)
            scores = EvaluationScores(
                evidence_quality=1.0 if "UVM_PASSED" in full_log or "PASSED" in full_log else 0.0,
                fix_plausibility=1.0 if success else 0.0,
                metadata={"exit_code": process.returncode},
                no_hallucinated_signals=1.0,
                root_cause_correct=1.0 if case.expected_fix_contains in proposed_fix else 0.0,
                tool_use_correctness=1.0
            )

            # 4. Trajectory Construction (Alignment with Trajectory Schema)
            trajectory = Trajectory(
                actions=[],
                case_id=case.id,
                constitutional_violations=[],
                evidence=[full_log],
                metadata={"run_id": run_id, "simulator": "icarus"},
                penalties=[],
                proposed_fix=proposed_fix,
                r_total=scores.fix_plausibility,
                root_cause="Derived from simulation log analysis.",
                scores=scores
            )

            # 5. Persistence
            save_eval_run(trajectory.model_dump())

            return trajectory

        finally:
            # Clean room protocol
            if work_dir.exists():
                shutil.rmtree(work_dir)