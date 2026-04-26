from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class AgentAction(BaseModel):
    input: str
    metadata: dict[str, Any] Field = (default_factory=dict)
    output: str
    step: int
    tool_name: str


class DVCase(BaseModel):
    bug_signature: str
    description: str
    expected_fix_contains: str | None = None
    expected_root_cause: str
    failure_coverage: float
    failure_log: str
    fix_replacement: str
    forbidden_targets: list[str]
    id: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    rtl: str
    success_coverage: float
    success_log: str
    testbench: str
    title: str    
    valid_signals: list[str]    


class EvaluationScores(BaseModel):
    evidence_quality: float = Field(ge=0.0, le=1.0)
    fix_plausibility: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] Field = (default_factory=dict)
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
    
   
   
