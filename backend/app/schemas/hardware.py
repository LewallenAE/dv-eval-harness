#!/usr/bin/env python3
"""
Immutable data contracts for hardware design validation and agentic telemetry.
Deterministic field ordering (Alphabetical) for consistent serialization.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
from typing import Any

# ----------------- Third Party Library -----------------
from pydantic import BaseModel, Field, ConfigDict

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------

class AgentAction(BaseModel):
    input: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    output: str
    step: int
    tool_name: str

class DVCase(BaseModel):
    """
    Schema for AXI-Lite Verification Cases. 
    Fields are ordered alphabetically for deterministic serialization.
    """
    bug_signature: str = Field(..., description="The UVM or Compiler error string.")
    description: str = Field(..., description="High-level overview of the failure mode.")
    expected_fix_contains: str = Field(..., description="Substring required in the passing fix.")
    expected_root_cause: str = Field(..., description="The logical explanation of the bug.")
    failure_coverage: float = Field(0.0, description="Functional coverage achieved by the buggy code.")
    failure_log: str = Field(..., description="Simulation log output showing the failure.")
    fix_replacement: str = Field(..., description="The corrected RTL code block.")
    forbidden_targets: list[str] = Field(default_factory=list, description="Signals the agent is NOT allowed to modify.")
    id: str = Field(..., description="Unique slug (e.g., 'AXI_LITE_001').")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Channel and bug type tags.")
    model_config = ConfigDict(populate_by_name=True)
    rtl: str = Field(..., description="The buggy Verilog/SystemVerilog source code.")
    success_coverage: float = Field(100.0, description="Target functional coverage for the fix.")
    success_log: str = Field(..., description="Simulation log output showing a successful run.")
    testbench: str = Field(..., description="The UVM/SystemVerilog task or sequence used for stimulus.") 
    title: str = Field(..., description="Human-readable title of the verification case.")
    valid_signals: list[str] = Field(default_factory=list, description="List of monitored signals for scoring.")

   

class EvaluationScores(BaseModel):
    evidence_quality: float = Field(ge=0.0, le=1.0)
    fix_plausibility: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    no_hallucinated_signals: float = Field(ge=0.0, le=1.0)
    root_cause_correct: float = Field(ge=0.0, le=1.0)    
    tool_use_correctness: float = Field(ge=0.0, le=1.0)

class Trajectory(BaseModel):
    actions: list[AgentAction]
    case_id: str
    constitutional_violations: list[str]
    evidence: list[str]
    metadata: dict[str, Any] = Field(default_factory=dict)
    penalties: list[str]
    proposed_fix: str
    r_total: float
    root_cause: str    
    scores: EvaluationScores