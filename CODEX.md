# CURRENT STATE OF THE REPO AND PROJECT

Critical Runtime Breaks (Fix These First — Won't Even Import/Run)

Missing run_agent_on_case function: Imported in smoke_test.py, backend/app/main.py, and app/api/v1/eval.py (e.g., from app.services.agent_runner import run_agent_on_case), but never defined. agent_runner.py only has class AgentRunner with async run_evaluation(...). This causes immediate ImportError/AttributeError.
Fix: Add a convenience wrapper in agent_runner.py:Pythondef run_agent_on_case(case: DVCase) -> Trajectory:
    runner = AgentRunner()
    # Note: make sync or use asyncio.run() carefully
    return asyncio.run(runner.run_evaluation(case, proposed_fix=...))  # or integrate proposal logic(Smoke test and API expect it to take a DVCase and return Trajectory.)
Undefined TRACE_FILE + duplicate code in backend/app/main.py (lines ~45-55): References non-existent TRACE_FILE, calls run_agent_on_case twice in /run-case, mixes sync/async.
Fix: Remove dead code; use local JSONL fallback or make Supabase optional.
Async/sync mismatch: run_evaluation is async def (uses asyncio.create_subprocess_exec + await), but called synchronously in FastAPI endpoints and smoke_test. Will hang or error.
storage.py hard dependency: Raises RuntimeError at import if no SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY. Roadmap calls this "integration" — make it optional with local JSONL persistence (title promises "JSONL trace persistence").

2. Integration & Logic Gaps (Core Flow Incomplete)

evaluator.py (full MOR/PRM/penalties) is under-used: agent_runner.py has its own simplistic hardcoded EvaluationScores (e.g., evidence_quality based only on "UVM_PASSED" in log) and ignores compute_r_total, compute_scores, compute_penalties, compute_prm_scores. The "Math Teacher" reward model in README isn't fully wired.
Fix: Refactor agent_runner.py to import and call the full evaluator logic (pass actions, evidence, proposed_fix, etc.). Use real r_total instead of just fix_plausibility.
Agent proposal step missing: README describes 5-step loop with "agent proposes logical fix", but code assumes proposed_fix is already provided (no LLM call, no tools.py integration for real inspection/proposal in the runner). DPO pair gen is standalone.
Fix: Add a simple agent step (e.g., stub or integrate with OpenAI/Anthropic) that uses tools.py (inspect_rtl, search_logs) + proposes via string replace or LLM.
Simulator adapters rough:
Cocotb: pytest --cocotb --simulator=icarus + env hacks may not work reliably (Cocotb prefers its own cocotb runner or Makefile). Icarus path is better but parses logs naively.
Mock is solid (uses tools.py).
Fix: Standardize on Makefile + cocotb-config (already partially in agent_runner), add real error handling, support more simulators per roadmap.

DPO pipeline partial: DPO_logic.py + DPO_pref_pair_gen.py exist and use torch, but not called from main flow/smoke_test/FastAPI. No end-to-end dataset gen.

3. Setup, Docs & Packaging Issues

Install broken per README: Says uv pip install -r requirements.txt + uv run smoke_test.py, but no requirements.txt (uses backend/pyproject.toml + duplicated uv.lock). Root has uv.lock too.
Fix: Update README; add uv sync or workspace setup; provide .env.example (for Supabase + optional OPENAI key); document sudo apt install iverilog.
Root main.py useless + duplication (.python-version, uv.lock in root + backend/). Clean to single entrypoint (e.g., uv run -m backend.app.main or CLI via typer).
Empty/placeholder files: backend/README.md (0B), some blueprint JSONs (0B), core/ mostly empty. Populate or remove.
No LICENSE, .github/ (workflows), CONTRIBUTING, or Docker. Add them (e.g., MIT license matching author credits).
README quickstart output outdated (shows R_Total: 0.93 ✓; actual smoke would fail currently).

4. Code Quality & Maintainability

Alphabetical obsession: Consistent but verbose (every function param/docstring repeats "alphabetized for determinism"). Use Pydantic model_config = ConfigDict(populate_by_name=True, frozen=True) + __init__.py re-exports more aggressively.
Error handling thin: Many subprocesses, tempdirs, no retries, broad excepts in API.
Hardcoded paths (e.g., /tmp/dv_eval_workspace, mock RTL in smoke_test cases).
Tests good but incomplete: test_evaluator.py is excellent (covers weights, word-boundary penalties, PRM stacking, clamping, tool ratio). Expand test_agent_runner.py and add integration tests.
Style: Mix of shebangs, future imports, blank sections. Run ruff/black; add type checking (pyright/mypy).
Security/Prod: Supabase service key exposed via env (fine for now); add config via pydantic-settings; logging (structlog?); rate limiting on API.

5. Feature/ Roadmap Gaps

No real LLM agent loop, no preference optimization training loop, no dashboard/leaderboard.
Limited cases (only 3 mock; blueprints underused).
No JSONL export (Supabase-only).
Expand to more protocols (AXI full, PCIe, etc.) via design_patterns.py.



More INfo

Different abstractions, different purposes, both useful, don't collapse them into one schema.
Concrete analogy:
DVCase is a row in a "bugs we found" spreadsheet. FIFOSchema is the entry in a design pattern library that says "this is what a correct FIFO looks like."
You need both. They serve different layers of the system.
How they actually compose in your harness:
DVCase (a specific FIFO bug)
  └─ rtl: buggy Verilog source
  └─ family: "fifo_buffer"
  └─ depth: 16, data_width: 8, pointer_width: 5
  └─ ...

FIFOSchema (the canonical design rules)
  └─ control_signals: must include clk, rst_n, wr_en, rd_en
  └─ status_flags: must implement full, empty
  └─ pointer_width formula: clog2(depth) + 1
  └─ uvm_model: uvm_reg_fifo

When the agent proposes a fix:
  1. Check it's a valid DVCase (the bug instance is well-formed)
  2. Check the proposed_fix conforms to FIFOSchema (the fix follows canonical rules)
  3. Reward signal includes "did the fix preserve canonical structure"
What this unlocks for your reward function:
This is actually a strong upgrade. Right now your compute_scores checks substring match on expected_fix_contains. With family schemas, you can check structural conformance:

FSMCase fix proposed — does the fix maintain has_default_case=True? Does it preserve the three-block structure? Does it keep encoding consistent?
FIFOCase fix proposed — does the fix preserve pointer_width = clog2(depth)+1? Does it touch status_flag logic correctly?
ArbiterCase fix proposed — does the fix preserve the sticky-until-transaction-end behavior?

These are structural checks, not substring checks. Much harder to game. Closer to what a real DV linter would catch.
My recommendation — use both, don't merge them:
Add the family schemas as a separate concept in your codebase. Suggested file structure:
backend/app/schemas/
  ├─ hardware.py         # DVCase, AgentAction, EvaluationScores, Trajectory (case data)
  └─ design_patterns.py  # FIFOSchema, FSMSchema, ArbiterSchema (canonical structure)
The case schema is what the harness ingests. The design pattern schema is what the fix validator checks against. Two separate consumers, two separate schemas, no confusion.
Small fix on NotebookLM's output before you use it:
A few things to clean up:

The Pydantic v2 alias syntax. NotebookLM wrote Field(..., alias="p_nbits") on data_width. That's fine if your blueprint JSONs actually use p_nbits as the key. If they use data_width, drop the alias.
pointer_width shouldn't be a free field. It's derived from depth: clog2(depth) + 1. Pydantic v2 has computed fields for this:

python   from pydantic import computed_field
   import math

   class FIFOSchema(BaseModel):
       depth: int
       
       @computed_field
       @property
       def pointer_width(self) -> int:
           return math.ceil(math.log2(self.depth)) + 1
Now pointer_width can't drift out of sync with depth. The system enforces the design rule, which is the whole point.

Defaults via mutable types. control_signals: List[str] = ["clk", ...] is a Pydantic v2 footgun for some types. Use Field(default_factory=lambda: ["clk", "rst_n", "wr_en", "rd_en"]) to be safe. Or just leave it — Pydantic v2 handles list defaults better than v1.
bit_width in FSMSchema is also derived. Same trick:

python   @computed_field
   @property
   def bit_width(self) -> int:
       if self.encoding_type == FSMStateEncoding.ONE_HOT:
           return len(self.states)
       return math.ceil(math.log2(len(self.states)))

Assertions as raw SystemVerilog strings is okay for now, but eventually you'd want them parsed/validated. Mark it as known limitation.

Cleaned-up version, combining NotebookLM's content with the v2 idioms:
python#!/usr/bin/env python3
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
The interview frame:
Now you have two schema layers, and you can talk about them as such:
"My DVCase schemas are discriminated unions on bug family — they describe specific instances. My design pattern schemas describe the canonical structure of each family — what a correct FIFO/FSM/arbiter looks like. The reward function uses both: substring/structural checks at the case level for whether the fix targets the right thing, and pattern-level checks for whether the fix preserves canonical structure. That second check is the one that catches the agent producing a 'fix' that passes simulation but violates design canon — which is exactly the synthesizability gap real DV teams care about."
That paragraph distinguishes you. You're not just doing functional verification — you're enforcing structural design rules, which is what senior DV engineers actually grade on.
How far to take this today:
If you want to add design pattern schemas, do FSMSchema and FIFOSchema only — they're the most useful for structural checks and they're cleanly defined. Skip ArbiterSchema for now (it's more nuanced and you don't have those cases yet anyway). 30-minute add.
If you don't want to add them today, that's also fine — they go in your "what's next" list as "Family-level design pattern schemas for structural conformance checks beyond functional simulation." Strong roadmap item.
What's your call — add them now, or note them and move forward?You said: Hold up so what happened to the DVCase?Hold up so what happened to the DVCase?4:46 PMClaude responded: Nothing happened to it — DVCase is still the right schema for case data.Nothing happened to it — DVCase is still the right schema for case data. I was poorly clear in the last message and made it sound like NotebookLM's schemas were replacing it. They're not. Let me draw the picture cleanly.
You have (or will have) two distinct schema files:
backend/app/schemas/
  ├─ hardware.py         ← DVCase lives here (the discriminated union I drafted earlier)
  └─ design_patterns.py  ← FIFOSchema/FSMSchema/ArbiterSchema would live here
What each one does:
hardware.py — DVCase and its subclasses (FIFOCase, FSMCase, ArbiterCase, AXILiteCase)
This is case data. Every row in your dataset is a DVCase. Has fields like rtl, failure_log, expected_fix_contains, expected_root_cause. The harness ingests these and runs trajectories against them. You absolutely need this. This is the schema you ship.
design_patterns.py — FIFOSchema, FSMSchema, ArbiterSchema
This is design canon. Describes what a correct FIFO/FSM/arbiter looks like in general — control signal naming, three-block FSM structure, sticky grant behavior. Optional. Adds structural validation as a layer.
Concrete picture:
A specific FIFO bug case (instance):
  DVCase → FIFOCase
    id: "FIFO_001"
    family: "fifo_buffer"
    depth: 16
    data_width: 8
    rtl: "<buggy verilog with overflow bug>"
    expected_fix_contains: "wr_ptr <= wr_ptr + 1"
    failure_log: "..."
    
The canonical FIFO design pattern (rules):
  FIFOSchema
    control_signals: ["clk", "rst_n", "wr_en", "rd_en"]
    status_flags: ["full", "empty"]
    pointer_width: clog2(depth) + 1  ← derived rule
    uvm_model: "uvm_reg_fifo"
Same hardware family, two different abstractions. The bug case says "this specific FIFO is broken in this specific way." The design pattern says "all FIFOs of this kind should look like this structurally."
Order of priority:

DVCase refactor (the discriminated union) — definitely ship this. This is the upgrade your harness actually needs because right now DVCase is AXI-Lite-shaped and your other three families don't fit cleanly.
Design pattern schemas — nice-to-have. Adds a structural validation layer to the reward function. Strong interview talking point. But not strictly required to apply Monday.

So: DVCase stays, gets the discriminated union refactor I drafted earlier. Design pattern schemas are a separate optional addition. They don't compete or overlap.
Make sense? If yes, the action item is the DVCase refactor on hardware.py — which is the file you pasted. The design pattern stuff is a separate file you might or might not add.