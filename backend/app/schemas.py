from __future__ import annotations

from pydantic import BaseModel, Field

class DVCase(BaseModel):
    # --- Core fields: must be present in every case (cannot be inferred) ---
    id: str
    rtl: str
    bug_signature: str
    # Optional: omit when the root cause is unknown (switches to Analysis mode)
    expected_root_cause: str = ""

    # --- Descriptive fields: inferred by LLM if absent ---
    title: str = ""
    description: str = ""
    testbench: str = ""
    fix_replacement: str = ""
    expected_fix_contains: str | None = None

    # --- Evaluation fields: inferred or defaulted if absent ---
    valid_signals: list[str] = Field(default_factory=list)
    forbidden_targets: list[str] = Field(default_factory=list)
    failure_log: str = ""
    success_log: str = ""
    failure_coverage: float = 0.0
    success_coverage: float = 100.0

class AgentAction(BaseModel):
    step: int
    tool_name: str
    input: str
    output: str

class EvaluationScores(BaseModel):
    # None when no expected_root_cause was provided (Analysis mode)
    root_cause_correct: float | None = Field(default=None, ge=0.0, le=1.0)
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
    # False when expected_root_cause was absent — agent output is the diagnosis, not scored
    eval_mode: bool = True
