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
from app.services.safety import (
    DEFAULT_SIMULATION_POLICY,
    SimulationPolicy,
    apply_process_memory_limit,
    parse_simulation_log,
    supports_process_limits,
    truncate_log,
)
from app.tools import run_mock_simulator

# ----------------- Module-level Configuration -----------------

class SimulationResult(BaseModel):
    """
    Normalized result container for all simulator backends.
    Fields are strictly alphabetized for deterministic serialization.
    """
    coverage: float
    exit_code: int | None = None
    log: str
    pass_rate: float
    raw_artifacts: dict[str, object] = Field(default_factory=dict)
    simulator_name: str
    timed_out: bool = False


class SimulatorAdapter(Protocol):
    """Common interface for hardware simulation execution."""

    def run(
        self,
        case: DVCase,
        rtl: str,
        policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
    ) -> SimulationResult:
        """Run a case against the provided RTL and return normalized results."""


def _run_subprocess(
    command: list[str],
    cwd: Path,
    policy: SimulationPolicy,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str] | subprocess.TimeoutExpired[str]:
    """Execute a simulator command with watchdog and optional memory limit."""
    def set_memory_limit() -> None:
        apply_process_memory_limit(policy)

    preexec_fn = set_memory_limit if supports_process_limits() else None
    return subprocess.run(
        command,
        capture_output=True,
        cwd=cwd,
        env=env,
        preexec_fn=preexec_fn,
        text=True,
        timeout=policy.timeout_seconds,
    )


class CocotbSimulatorAdapter:
    """
    The 'Neural Bridge' adapter.
    Executes Python-based testbenches via Cocotb/pyuvm and Icarus Verilog.
    """
    simulator_name: str = "cocotb"

    def run(
        self,
        case: DVCase,
        rtl: str,
        policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
    ) -> SimulationResult:
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

            run_res = _run_subprocess(run_cmd, tmp_path, policy, env=env)

            if isinstance(run_res, subprocess.TimeoutExpired):
                return SimulationResult(
                    coverage=0.0,
                    exit_code=None,
                    log=truncate_log(f"SIMULATION TIMEOUT after {policy.timeout_seconds}s", policy),
                    pass_rate=0.0,
                    raw_artifacts={"policy": policy.model_dump(), "timeout": True},
                    simulator_name=self.simulator_name,
                    timed_out=True,
                )

            combined_log = truncate_log(run_res.stdout + run_res.stderr, policy)
            passed = "passed" in combined_log.lower() and "error" not in combined_log.lower()
            summary = parse_simulation_log(combined_log)

            return SimulationResult(
                coverage=summary.coverage_percent if summary.coverage_percent is not None else 100.0 if passed else 0.0,
                exit_code=run_res.returncode,
                log=combined_log,
                pass_rate=1.0 if passed else 0.0,
                raw_artifacts={"policy": policy.model_dump(), "uvm_summary": summary.model_dump()},
                simulator_name=self.simulator_name,
            )


class IcarusSimulatorAdapter:
    """The 'Metal' adapter that executes actual Icarus Verilog simulations."""
    simulator_name: str = "icarus"

    def run(
        self,
        case: DVCase,
        rtl: str,
        policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
    ) -> SimulationResult:
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

            compile_res = _run_subprocess(compile_cmd, tmp_path, policy)

            if isinstance(compile_res, subprocess.TimeoutExpired):
                return SimulationResult(
                    coverage=0.0,
                    exit_code=None,
                    log=truncate_log(f"COMPILATION TIMEOUT after {policy.timeout_seconds}s", policy),
                    pass_rate=0.0,
                    raw_artifacts={"policy": policy.model_dump(), "timeout": True},
                    simulator_name=self.simulator_name,
                    timed_out=True,
                )

            if compile_res.returncode != 0:
                combined_log = truncate_log(f"COMPILATION ERROR:\n{compile_res.stderr}", policy)
                return SimulationResult(
                    coverage=0.0,
                    exit_code=compile_res.returncode,
                    log=combined_log,
                    pass_rate=0.0,
                    raw_artifacts={
                        "policy": policy.model_dump(),
                        "uvm_summary": parse_simulation_log(combined_log).model_dump(),
                    },
                    simulator_name=self.simulator_name
                )

            # 2. VVP Execution Command
            run_cmd = ["vvp", str(out_file)]
            run_res = _run_subprocess(run_cmd, tmp_path, policy)

            if isinstance(run_res, subprocess.TimeoutExpired):
                return SimulationResult(
                    coverage=0.0,
                    exit_code=None,
                    log=truncate_log(f"SIMULATION TIMEOUT after {policy.timeout_seconds}s", policy),
                    pass_rate=0.0,
                    raw_artifacts={"policy": policy.model_dump(), "timeout": True},
                    simulator_name=self.simulator_name,
                    timed_out=True,
                )

            # 3. Deterministic Log Parsing
            combined_log = truncate_log(run_res.stdout + run_res.stderr, policy)
            passed = "UVM_PASSED" in combined_log or "Test Passed" in combined_log
            summary = parse_simulation_log(combined_log)

            return SimulationResult(
                coverage=summary.coverage_percent if summary.coverage_percent is not None else 100.0 if passed else 0.0,
                exit_code=run_res.returncode,
                log=combined_log,
                pass_rate=1.0 if passed else 0.0,
                raw_artifacts={"policy": policy.model_dump(), "uvm_summary": summary.model_dump()},
                simulator_name=self.simulator_name,
            )


class MockSimulatorAdapter:
    """Deterministic adapter used for demo and local development."""
    simulator_name: str = "mock"

    def run(
        self,
        case: DVCase,
        rtl: str,
        policy: SimulationPolicy = DEFAULT_SIMULATION_POLICY,
    ) -> SimulationResult:
        result = run_mock_simulator(case, rtl)
        log = truncate_log(result["log"], policy)
        summary = parse_simulation_log(log)
        return SimulationResult(
            coverage=summary.coverage_percent if summary.coverage_percent is not None else result["coverage"],
            exit_code=0,
            log=log,
            pass_rate=result["pass_rate"],
            raw_artifacts={"policy": policy.model_dump(), "uvm_summary": summary.model_dump()},
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
