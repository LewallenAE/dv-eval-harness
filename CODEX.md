You are working in my local project: dv-agent-eval.

Goal: Refactor this from a hardcoded mock demo into a semi-production configurable DV agent evaluation harness.

Current backend structure:
backend/
  app/
    main.py
    schemas.py
    evaluator.py
    tools.py
    agent_runner.py
  mock_cases/
  traces/

Do the following carefully.

1. Update app/schemas.py

Extend DVCase with these fields:
- bug_signature: str
- fix_replacement: str
- failure_log: str
- success_log: str
- failure_coverage: float
- success_coverage: float
- expected_fix_contains: str | None = None

Keep existing fields:
- id
- title
- description
- rtl
- testbench
- expected_root_cause
- valid_signals
- forbidden_targets

Make sure all Pydantic models have correct field spelling:
- AgentAction.output
- EvaluationScores.tool_use_correctness

2. Refactor app/tools.py

Change the tool functions so they are case-driven instead of hardcoded.

Required functions:

- inspect_rtl(case: DVCase, rtl: str) -> str
  - If case.bug_signature is present in rtl, return a finding that the configured bug signature was detected.
  - Otherwise return that no configured bug signature was detected.
  - Mention the case id/title in the summary.

- run_mock_simulator(case: DVCase, rtl: str) -> dict[str, Any]
  - If case.bug_signature exists in rtl, return:
    {
      "log": case.failure_log,
      "coverage": case.failure_coverage,
      "pass_rate": 0.60
    }
  - Else return:
    {
      "log": case.success_log,
      "coverage": case.success_coverage,
      "pass_rate": 0.95
    }

- propose_fix(case: DVCase, rtl: str) -> str
  - Replace case.bug_signature with case.fix_replacement.
  - If bug_signature is not found, return rtl unchanged.

- search_logs(sim_log: str) -> str
  - Extract lines containing UVM_ERROR, UVM_FATAL, ASSERTION FAILED, ERROR, FATAL.
  - If none found, return "No critical simulator failures found."

3. Refactor app/agent_runner.py

Update run_agent_on_case(case: DVCase) so it calls:
- run_mock_simulator(case, case.rtl)
- search_logs(...)
- inspect_rtl(case, case.rtl)
- propose_fix(case, case.rtl)
- run_mock_simulator(case, fixed_rtl)

The predicted root cause can still be case.expected_root_cause for MVP, but add a comment explaining that this will later be replaced by LLM inference.

Use the existing evaluator to compute scores and r_total.

4. Update app/evaluator.py

Make fix_plausibility configurable:
- If expected_fix_contains exists and appears in proposed_fix, score 1.0.
- Else if "<=" or "nonblocking" appears, score 0.8.
- Else score 0.5.

Keep the scalar formula:
R_total =
0.30 root_cause_correct
+ 0.25 evidence_quality
+ 0.20 tool_use_correctness
+ 0.15 fix_plausibility
+ 0.10 no_hallucinated_signals
minus penalties.

Keep forbidden target penalty.

5. Update app/main.py

Keep endpoints:
- GET /
- GET /cases
- POST /run-case/{case_id}

Add:
- GET /traces
  - Reads backend/traces/eval_runs.jsonl
  - Returns [] if no file exists
  - Returns list[dict] otherwise

Make sure path handling uses pathlib and works when running from backend with:
uvicorn app.main:app --reload

6. Update mock_cases/fsm_stuck_bug.json

Add the new fields:
"bug_signature": "state = BUSY",
"fix_replacement": "state <= BUSY",
"failure_log": "UVM_ERROR: FSM remained in IDLE after start asserted.\nASSERTION FAILED: expected state transition IDLE -> BUSY.\nCOVERAGE: 42.0",
"success_log": "UVM_INFO: All checks passed.\nASSERTION PASSED: expected state transition observed.\nCOVERAGE: 87.5",
"failure_coverage": 42.0,
"success_coverage": 87.5,
"expected_fix_contains": "state <= BUSY"

7. Add two additional mock cases:

mock_cases/axi_handshake_bug.json
- Bug: valid signal drops before ready is asserted.
- bug_signature: "valid = 0"
- fix_replacement: "valid <= valid && !ready"
- expected_root_cause: "valid drops before ready in AXI-style handshake"
- valid_signals: ["clk", "reset_n", "valid", "ready", "data"]
- expected_fix_contains: "valid <= valid && !ready"

mock_cases/uart_overflow_bug.json
- Bug: FIFO write pointer increments without checking full.
- bug_signature: "wr_ptr <= wr_ptr + 1"
- fix_replacement: "if (!fifo_full) wr_ptr <= wr_ptr + 1"
- expected_root_cause: "UART FIFO write pointer increments while FIFO is full"
- valid_signals: ["clk", "reset_n", "rx_valid", "fifo_full", "wr_ptr"]
- expected_fix_contains: "if (!fifo_full) wr_ptr <= wr_ptr + 1"

Make each JSON valid and complete.

8. Add tests if pytest is installed, otherwise skip tests but do not break the app.

If adding tests:
backend/tests/test_evaluator.py
backend/tests/test_agent_runner.py

Test:
- fsm_stuck_bug produces r_total >= 0.8
- proposed_fix contains expected_fix_contains
- /cases returns all three cases
- /traces returns list

9. After changes, run:
python -m compileall app

Then tell me:
- files changed
- exact commands to run
- any tests added
- any assumptions made

Do not over-engineer. Do not add LangChain. Do not add real LLM calls. Do not add real EDA integration. Keep this deterministic, configurable, and interview-demo ready.




Add a simulator adapter abstraction.

Create app/simulators.py with:

- SimulatorAdapter Protocol
- MockSimulatorAdapter
- get_simulator_adapter(name: str = "mock")

The adapter must expose:
run(case: DVCase, rtl: str) -> SimulationResult

SimulationResult should be a Pydantic model or dataclass with:
- log: str
- coverage: float
- pass_rate: float
- simulator_name: str
- raw_artifacts: dict[str, str] = {}

Refactor agent_runner.py so it does not call run_mock_simulator directly. It should use:

simulator = get_simulator_adapter("mock")
sim_before = simulator.run(case, case.rtl)
sim_after = simulator.run(case, fixed_rtl)

Keep the mock deterministic. Do not add real Questa/VCS integration yet.

Add comments/docstrings showing how a QuestaSimulatorAdapter or VCSSimulatorAdapter would later implement the same interface.

Goal: make the architecture production-shaped without requiring commercial EDA tools.