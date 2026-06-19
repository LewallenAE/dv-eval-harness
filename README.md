# DV Agent Eval Harness

An evaluation harness for LLM-based RTL debug agents. The system runs an agent through a structured debug pipeline on SystemVerilog bug cases, scores its output across five reward dimensions, and persists JSONL traces suitable for DPO/GRPO training data generation.

---

## What It Does

Given a buggy RTL snippet, the agent:

1. Runs the simulator on the buggy RTL
2. Searches the simulation log for failure evidence
3. Inspects the RTL for the bug signature
4. Proposes a fix
5. Re-runs the simulator to verify

The harness scores the full trajectory and emits a decomposed scalar reward.

---

## Reward Function

| Dimension | Weight (Eval) | Weight (Analysis) |
|---|---|---|
| Root Cause Semantic Match | 0.30 | — redistributed |
| Evidence Quality | 0.25 | 0.36 |
| Tool Use Correctness | 0.20 | 0.29 |
| Fix Plausibility | 0.15 | 0.21 |
| Signal Integrity | 0.10 | 0.14 |

**Eval mode** — `expected_root_cause` provided. Root cause match is scored by an LLM judge (semantic similarity, not string equality).

**Analysis mode** — no ground truth. Agent produces a diagnosis; root-cause weight redistributes across the other four dimensions.

Fix plausibility hierarchy: exact token match → 1.0, simulator passes post-fix → 0.9, non-blocking assignment pattern present → 0.8, else → 0.5.

Penalty: −0.30 per `forbidden_target` modified.

---

## Case Library

204 SystemVerilog bug cases across four architectures:

| Architecture | Cases | Bug Classes |
|---|---|---|
| AXI-Lite | 50 | Protocol violations, handshake bugs, CDC, timing |
| Round-Robin Arbiter | 77 | Fairness, pointer bugs, reset, one-hot violations |
| FSM | 44 | Latch inference, missing default, deadlock, Mealy races |
| FIFO | 30 | Pointer reset, full/empty logic, overflow |

All RTL is synthesizable SystemVerilog. Every case includes `failure_log`, `success_log`, `expected_root_cause`, and full scoring metadata. Cases without `expected_root_cause` run in Analysis mode.

---

## Simulator Boundary

The agent runner, evaluator, and trace store depend only on a stable `SimulationResult` interface. The current implementation uses a deterministic mock — no EDA license required. Swapping in Questa, VCS, or any other simulator is an adapter implementation against the existing `SimulatorAdapter` protocol.

---

## Stack

```
frontend/     Next.js 16 · React 19 · Tailwind v4
backend/      FastAPI · Pydantic v2 · Python 3.12
              Anthropic SDK (root cause inference + LLM judge)
traces/       JSONL — one line per trajectory
```

---

## Quick Start

### Docker

```bash
cp backend/.env.example backend/.env
# set ANTHROPIC_API_KEY in backend/.env

docker-compose up
```

API at `http://localhost:8000`. Traces volume-mount to `backend/traces/` and persist across restarts.

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
| `POST` | `/ingest-case` | Upload raw JSON; LLM fills missing fields |
| `GET` | `/traces` | Return all scored trajectories |

### Minimum Case Payload

```json
{
  "id": "MY_BUG_001",
  "rtl": "assign full = (wr_ptr == rd_ptr);",
  "bug_signature": "UVM_ERROR: FIFO overflow detected"
}
```

Omit `expected_root_cause` for Analysis mode. Include it for Eval mode. All other fields are optional — the LLM fills them in automatically via `/ingest-case`.

---

## JSONL Traces

Each run appends one line to `backend/traces/eval_runs.jsonl`:

```jsonl
{"case_id": "AXI_LITE_001", "root_cause": "...", "proposed_fix": "...", "scores": {"root_cause_correct": 1.0, "evidence_quality": 1.0, ...}, "r_total": 0.92, "eval_mode": true}
```

Each trajectory contains the full signal needed to construct DPO chosen/rejected pairs or GRPO group rollouts.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (for LLM features) | Root cause inference and LLM judge |
| `DV_LLM_MODEL` | No | Model override (default: `claude-sonnet-4-6`) |

Without an API key the harness runs fully offline — inference returns the configured ground truth and scoring falls back to substring match.

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
    agent_runner.py  # Debug pipeline
    evaluator.py     # Reward decomposition and R-total
    tools.py         # Simulator, RTL inspection, bug detection
    llm.py           # Root cause inference, LLM judge, case normalization
    schemas.py       # DVCase, Trajectory, EvaluationScores (Pydantic)
    simulators.py    # SimulatorAdapter protocol
  mock_cases/        # 204 bug cases organized by architecture
  traces/            # JSONL run output (gitignored)

frontend/
  app/               # Next.js app router pages
  components/        # ScoreCard, TrajectoryViewer, CaseUploader
  lib/               # API client, TypeScript types
```
