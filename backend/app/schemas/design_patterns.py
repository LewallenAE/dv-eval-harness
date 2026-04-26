#!/usr/bin/env python3
"""
Canonical design pattern schemas for hardware families.
Used to validate that generated/proposed RTL conforms to family rules.
Distinct from DVCase, which describes a specific bug instance.
"""

# ----------------- Futures -----------------
from __future__ import annotations

# ----------------- Standard Library -----------------
import math
from enum import Enum

# ----------------- Third Party Library -----------------
from pydantic import BaseModel, Field, computed_field

# ----------------- Application Imports -----------------


# ----------------- Module-level Configuration -----------------


class FSMStateEncoding(str, Enum):
    ONE_HOT = "one_hot"
    BINARY = "binary"
    GRAY = "gray"


class FIFOSchema(BaseModel):
    """Canonical structure for synchronous FIFO buffers."""

    control_signals: list[str] = Field(default_factory=lambda: ["clk", "rst_n", "wr_en", "rd_en"])
    data_signals: list[str] = Field(default_factory=lambda: ["wr_data", "rd_data"])
    data_width: int = Field(..., gt=0, description="Width of the data bus in bits.")
    depth: int = Field(..., gt=0, description="Number of FIFO entries.")
    id: str = Field(..., description="Unique identifier for this FIFO skill entry.")
    is_synchronous: bool = True
    status_flags: list[str] = Field(default_factory=lambda: ["full", "empty"])
    uvm_model: str = "uvm_reg_fifo"

    @computed_field
    @property
    def pointer_width(self) -> int:
        """clog2(depth) + 1 — extra bit distinguishes full from empty."""
        return math.ceil(math.log2(self.depth)) + 1


class FSMSchema(BaseModel):
    """Canonical three-block stylized FSM structure."""

    encoding_type: FSMStateEncoding = FSMStateEncoding.BINARY
    explicit_base_type: str = "logic"
    has_combinational_next_state: bool = True
    has_combinational_output_logic: bool = True
    has_default_case: bool = True
    has_sequential_state_reg: bool = True
    id: str
    states: list[str] = Field(..., min_length=2, description="Named state labels.")

    @computed_field
    @property
    def bit_width(self) -> int:
        """Width of the state register, derived from encoding and state count."""
        if self.encoding_type == FSMStateEncoding.ONE_HOT:
            return len(self.states)
        return max(1, math.ceil(math.log2(len(self.states))))


class ArbiterSchema(BaseModel):
    """Canonical round-robin arbiter with sticky grant and last-granted state."""

    assertions: list[str] = Field(
        default_factory=lambda: [
            "property one_hot_grant; $onehot0(gnt); endproperty",
            "property no_premature_revoke; $rose(gnt) |-> gnt throughout transaction_active; endproperty",
        ]
    )
    fairness_algorithm: str = "round_robin"
    grant_signals: list[str] = Field(..., description="One grant signal per master.")
    id: str
    is_sticky: bool = True
    num_masters: int = Field(..., gt=1)
    request_signals: list[str] = Field(..., description="One request signal per master.")
    storage_signals: list[str] = Field(default_factory=lambda: ["last_gnt_id"])
    termination_signal: str = Field(..., description="Signal that revokes grant (e.g., BVALID/RVALID).")