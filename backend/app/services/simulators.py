#!/usr/bin/env python3
"""
Hardware simulation abstraction layer (HAL) for EDA tool-agnostic runs.
Supports Mock, Icarus Verilog (Metal), and Cocotb/pyuvm (Neural Bridge) backends.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol

# ----------------- Third Party Library -----------------
from pydantic import BaseModel, Field

# ----------------- Application Imports -----------------
from app.schemas.hardware import DVCase
from app.tools import run_mock_simulator

# ----------------- Module-level Configuration -----------------

class SimulationResult(BaseModel):
    """
    Normalized result container for all simulator backends.
    Fields are strictly alphabetized for deterministic serialization.
    """
    coverage: float
    log: str
    pass_rate: float
    raw_artifacts: dict[str, str] = Field(default_factory=dict)
    simulator_name: str


class SimulatorAdapter(Protocol):
    """Common interface for hardware simulation execution."""

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        """Run a case against the provided RTL and return normalized results."""


class CocotbSimulatorAdapter:
    """
    The 'Neural Bridge' adapter.
    Executes Python-based testbenches via Cocotb/pyuvm and Icarus Verilog.
    """
    simulator_name: str = "cocotb"

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Alphabetized file definitions
            python_tb = tmp_path / "testbench.py"
            rtl_file = tmp_path / "design.sv"
            
            # Write assets to clean-room environment
            python_tb.write_text(case.testbench)
            rtl_file.write_text(rtl)

            # Alphabetized Environment Configuration
            env = os.environ.copy()
            env["MODULE"] = "testbench"
            env["PYTHONPATH"] = f"{tmp_path}:{env.get('PYTHONPATH', '')}"
            env["TOPLEVEL"] = case.metadata.get("toplevel", "top")

            # Command: Triggering the Python-to-Metal Handshake
            run_cmd = [
                "pytest", 
                "--cocotb", 
                "--simulator=icarus", 
                str(rtl_file)
            ]

            run_res = subprocess.run(
                run_cmd, 
                capture_output=True, 
                cwd=tmp_path, 
                env=env, 
                text=True
            )

            combined_log = run_res.stdout + run_res.stderr
            passed = "passed" in combined_log.lower() and "error" not in combined_log.lower()

            return SimulationResult(
                coverage=100.0 if passed else 0.0,
                log=combined_log,
                pass_rate=1.0 if passed else 0.0,
                raw_artifacts={},
                simulator_name=self.simulator_name,
            )


class IcarusSimulatorAdapter:
    """The 'Metal' adapter that executes actual Icarus Verilog simulations."""
    simulator_name: str = "icarus"

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Alphabetized file path definitions
            out_file = tmp_path / "sim.out"
            rtl_file = tmp_path / "design.sv"
            tb_file = tmp_path / "testbench.sv"

            # Write assets
            rtl_file.write_text(rtl)
            tb_file.write_text(case.testbench)

            # 1. Compile Command (iverilog)
            compile_cmd = [
                "iverilog",
                "-g2012",
                "-o", str(out_file),
                str(rtl_file),
                str(tb_file)
            ]

            compile_res = subprocess.run(compile_cmd, capture_output=True, text=True)

            if compile_res.returncode != 0:
                return SimulationResult(
                    coverage=0.0,
                    log=f"COMPILATION ERROR:\n{compile_res.stderr}",
                    pass_rate=0.0,
                    raw_artifacts={},
                    simulator_name=self.simulator_name
                )

            # 2. VVP Execution Command
            run_cmd = ["vvp", str(out_file)]
            run_res = subprocess.run(run_cmd, capture_output=True, text=True)

            # 3. Deterministic Log Parsing
            combined_log = run_res.stdout + run_res.stderr
            passed = "UVM_PASSED" in combined_log or "Test Passed" in combined_log

            return SimulationResult(
                coverage=100.0 if passed else 0.0,
                log=combined_log,
                pass_rate=1.0 if passed else 0.0,
                raw_artifacts={},
                simulator_name=self.simulator_name,
            )


class MockSimulatorAdapter:
    """Deterministic adapter used for demo and local development."""
    simulator_name: str = "mock"

    def run(self, case: DVCase, rtl: str) -> SimulationResult:
        result = run_mock_simulator(case, rtl)
        return SimulationResult(
            coverage=result["coverage"],
            log=result["log"],
            pass_rate=result["pass_rate"],
            raw_artifacts={},
            simulator_name=self.simulator_name,
        )


def get_simulator_adapter(name: str = "mock") -> SimulatorAdapter:
    """Factory to retrieve alphabetized simulator adapters."""
    normalized_name = name.lower().strip()
    
    if normalized_name == "cocotb":
        return CocotbSimulatorAdapter()
    
    if normalized_name == "icarus":
        return IcarusSimulatorAdapter()
    
    if normalized_name == "mock":
        return MockSimulatorAdapter()
        
    raise ValueError(f"Unsupported simulator adapter: {name}")