# DV Agent Eval Harness

A production-shaped evaluation harness for LLM-based RTL debug agents. The system runs an agent through a five-step debug pipeline on real SystemVerilog bug cases, scores its output across five reward dimensions, and persists DPO-ready JSONL traces.

Built as a portfolio project demonstrating full-stack AI/ML systems engineering at the hardware verification domain boundary.

---

## What It Does

You give the harness a buggy RTL snippet. The agent:

1. Runs the mock simulator on the buggy RTL
2. Searches the simulation log for failure evidence
3. Inspects the RTL for the bug signature
4. Proposes a fix
5. Re-runs the simulator to verify the fix

The harness scores the entire trajectory and produces a decomposed reward signal.

---

## Reward Function

| Dimension | Weight (Eval) | Weight (Analysis) |
|---|---|---|
| Root Cause Semantic Match | 0.30 | — redistributed |
| Evidence Quality | 0.25 | 0.36 |
| Tool Use Correctness | 0.20 | 0.29 |
| Fix Plausibility | 0.15 | 0.21 |
| Signal Integrity | 0.10 | 0.14 |

**Eval mode** — `expected_root_cause` provided. Agent is scored against ground truth using an LLM judge for semantic match (not string equality).

**Analysis mode** — no ground truth. Agent diagnoses the bug; root-cause weight redistributes across the other four dimensions.

Fix plausibility uses a priority hierarchy: exact token match → 1.0, simulator passes post-fix → 0.9, contains non-blocking assignment pattern → 0.8, else → 0.5.

---

## Case Library

204 hand-crafted SystemVerilog bug cases across four architectures:

| Architecture | Cases | Bug Classes |
|---|---|---|
| AXI-Lite | 50 | Protocol violations, handshake bugs, CDC, timing |
| Round-Robin Arbiter | 77 | Fairness, pointer bugs, reset, one-hot violations |
| FSM | 44 | Latch inference, missing default, deadlock, Mealy races |
| FIFO | 30 | Pointer reset, full/empty logic, overflow |

All RTL is synthesizable SystemVerilog. Bug signatures are UVM/VCS-style error strings. Every case has `failure_log`, `success_log`, `expected_root_cause`, and scoring metadata.

---

## Simulator Adapter Boundary

The harness does not depend on proprietary EDA tools. The agent runner, evaluator, and trace store consume a stable `SimulationResult` interface. The current implementation uses a deterministic mock simulator. Replacing it with Questa, VCS, or any other simulator is an adapter implementation — not a system rewrite.

---

## Stack

```
frontend/     Next.js 16 · React 19 · Tailwind v4
backend/      FastAPI · Pydantic v2 · Python 3.12
              Anthropic SDK (root cause inference + LLM judge)
traces/       JSONL — one line per trajectory, DPO-ready
```

---

## Quick Start

### Docker (recommended)

```bash
cp backend/.env.example backend/.env
# add your ANTHROPIC_API_KEY to backend/.env

docker-compose up
```

API available at `http://localhost:8000`. Traces are volume-mounted and persist across container restarts.

### Local Dev

```bash
# Backend
cd backend
pip install -e .
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/cases` | List all case IDs |
| `POST` | `/run-case/{case_id}` | Run agent on a stored case |
| `POST` | `/run-case-json` | Run agent on an inline DVCase payload |
| `POST` | `/ingest-case` | Upload raw JSON, LLM normalizes missing fields |
| `GET` | `/traces` | Return all scored trajectories |

### Upload Your Own Case

Minimum required fields:

```json
{
  "id": "MY_BUG_001",
  "rtl": "assign full = (wr_ptr == rd_ptr);",
  "bug_signature": "UVM_ERROR: FIFO overflow detected"
}
```

Omit `expected_root_cause` to run in Analysis mode. Include it to run in Eval mode and score against ground truth. Missing optional fields are filled in automatically by the LLM.

---

## JSONL Traces

Every run appends a trajectory to `backend/traces/eval_runs.jsonl`:

```jsonl
{"case_id": "AXI_LITE_001", "root_cause": "...", "proposed_fix": "...", "scores": {"root_cause_correct": 1.0, "evidence_quality": 1.0, ...}, "r_total": 0.92, "eval_mode": true}
```

Format is DPO-ready: each line contains the full signal needed to construct chosen/rejected pairs for preference model training.

---

## Environment

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (for LLM features) | Used for root cause inference and the LLM judge |
| `DV_LLM_MODEL` | No | Override the model (default: `claude-sonnet-4-6`) |

Without an API key the harness runs in mock mode — root cause inference returns the configured ground truth and scoring falls back to substring match instead of the semantic LLM judge.

---

## Kubernetes

```bash
kubectl apply -k k8s/
```

Manifests in `k8s/` cover namespace, deployment, service, ingress, PVC for trace persistence, and a secret template for the API key.

---

## Project Structure

```
backend/
  app/
    main.py          # FastAPI routes
    agent_runner.py  # Five-step debug pipeline
    evaluator.py     # Reward decomposition + R-total
    tools.py         # Simulator adapter, RTL inspection, bug detection
    llm.py           # Root cause inference, LLM judge, case normalization
    schemas.py       # DVCase, Trajectory, EvaluationScores (Pydantic)
    simulators.py    # Simulator adapter boundary
  mock_cases/        # 204 bug cases organized by architecture
  traces/            # JSONL run output (gitignored)

frontend/
  app/               # Next.js app router pages
  components/        # ScoreCard, TrajectoryViewer, CaseUploader
  lib/               # API client, TypeScript types
```
