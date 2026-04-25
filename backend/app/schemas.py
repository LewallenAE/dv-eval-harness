from __future__ import annotations

from pydantic import BaseModel, Field

class DVCase(BaseModel):
    id: str
    title: str
    description: str
    rtl: str
    testbench: str
    expected_root_cause: str
    valid_signals: list[str]
    forbidden_targets: list[str]
    bug_signature: str
    fix_replacement: str
    failure_log: str
    success_log: str
    failure_coverage: float
    success_coverage: float
    expected_fix_contains: str | None = None

class AgentAction(BaseModel):
    step: int
    tool_name: str
    input: str
    output: str

class EvaluationScores(BaseModel):
    root_cause_correct: float = Field(ge=0.0, le=1.0)
    evidence_quality: float = Field(ge=0.0, le=1.0)
    tool_use_correctness: float = Field(ge=0.0, le=1.0)
    fix_plausibility: float = Field(ge=0.0, le=1.0)
    no_hallucinated_signals: float = Field(ge=0.0, le=1.0)
    
class Trajectory(BaseModel):
    case_id: str
    root_cause: str
    proposed_fix: str
    actions: list[AgentAction]
    evidence: list[str]
    scores: EvaluationScores
    penalties: list[str]
    constitutional_violations: list[str]
    r_total: float
