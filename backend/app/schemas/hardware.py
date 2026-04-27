#!/usr/bin/env python3
"""
Immutable data contracts for hardware design validation and agentic telemetry.
Deterministic field ordering (Alphabetical) for consistent serialization.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import math
from enum import Enum
from typing import Annotated, Any, Literal

# ----------------- Third Party Library -----------------
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, computed_field

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------

class AgentAction(BaseModel):
    input: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    output: str
    step: int
    tool_name: str


class CaseFamily(str, Enum):
    ARBITER = "arbiter"
    AXI_LITE = "axi_lite"
    FIFO_BUFFER = "fifo_buffer"
    FSM_CONTROLLER = "fsm_controller"
    GENERIC = "generic"


class DVCase(BaseModel):
    """
    Base schema for a concrete hardware bug instance.
    Fields are ordered alphabetically for deterministic serialization.
    """
    bug_signature: str = Field(..., description="The UVM or Compiler error string.")
    description: str = Field(..., description="High-level overview of the failure mode.")
    expected_fix_contains: str = Field(..., description="Substring required in the passing fix.")
    expected_root_cause: str = Field(..., description="The logical explanation of the bug.")
    family: CaseFamily = Field(CaseFamily.GENERIC, description="Hardware design family for this case.")
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


class ArbiterCase(DVCase):
    family: Literal[CaseFamily.ARBITER] = CaseFamily.ARBITER
    fairness_algorithm: str = "round_robin"
    grant_signals: list[str] = Field(default_factory=list)
    is_sticky: bool = True
    num_masters: int | None = Field(default=None, gt=1)
    request_signals: list[str] = Field(default_factory=list)
    termination_signal: str | None = None


class AXILiteCase(DVCase):
    address_width: int | None = Field(default=None, gt=0)
    channel: str | None = None
    data_width: int | None = Field(default=None, gt=0)
    family: Literal[CaseFamily.AXI_LITE] = CaseFamily.AXI_LITE


class FIFOCase(DVCase):
    data_width: int | None = Field(default=None, gt=0)
    depth: int | None = Field(default=None, gt=0)
    family: Literal[CaseFamily.FIFO_BUFFER] = CaseFamily.FIFO_BUFFER

    @computed_field
    @property
    def pointer_width(self) -> int | None:
        """clog2(depth) + 1 when depth is provided."""
        if self.depth is None:
            return None
        return math.ceil(math.log2(self.depth)) + 1


class FSMCase(DVCase):
    encoding_type: str = "binary"
    family: Literal[CaseFamily.FSM_CONTROLLER] = CaseFamily.FSM_CONTROLLER
    states: list[str] = Field(default_factory=list)


class GenericDVCase(DVCase):
    family: Literal[CaseFamily.GENERIC] = CaseFamily.GENERIC


HardwareCase = Annotated[
    ArbiterCase | AXILiteCase | FIFOCase | FSMCase | GenericDVCase,
    Field(discriminator="family"),
]
HardwareCaseAdapter = TypeAdapter(HardwareCase)


def infer_case_family(data: dict[str, Any]) -> CaseFamily:
    """Infer legacy fixture family when no explicit discriminator is present."""
    raw_family = data.get("family")
    if raw_family:
        return CaseFamily(raw_family)

    haystack = " ".join(
        str(value).lower()
        for value in (
            data.get("id", ""),
            data.get("title", ""),
            data.get("description", ""),
            data.get("metadata", {}).get("category", ""),
            data.get("metadata", {}).get("interface", ""),
        )
    )
    if "axi" in haystack:
        return CaseFamily.AXI_LITE
    if "fifo" in haystack or "uart" in haystack or "buffer" in haystack:
        return CaseFamily.FIFO_BUFFER
    if "fsm" in haystack or "state" in haystack:
        return CaseFamily.FSM_CONTROLLER
    if "arb" in haystack or "grant" in haystack:
        return CaseFamily.ARBITER
    return CaseFamily.GENERIC


def parse_dv_case(data: dict[str, Any]) -> HardwareCase:
    """Validate a hardware case, adding a discriminator for legacy fixtures."""
    return HardwareCaseAdapter.validate_python(
        {**data, "family": infer_case_family(data)}
    )


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
