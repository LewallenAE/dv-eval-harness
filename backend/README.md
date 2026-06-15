# DV Agent Eval Harness

A configurable, deterministic evaluation harness for design-verification (DV) debug agents. Scores an agent's ability to identify RTL bugs, propose fixes, and cite simulation evidence — without requiring commercial EDA tools.

## Setup

```bash
# From the repo root
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e "backend[dev]"
```

## Run the API

```bash
cd backend
uvicorn app.main:app --reload
```

Endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `GET` | `/cases` | List available case IDs |
| `POST` | `/run-case/{case_id}` | Run a case and return scored trajectory |
| `GET` | `/traces` | Return all stored evaluation runs |

## Docker

```bash
# Copy env file and add your key
cp .env.example .env

# Build and run
docker compose up --build

# Run in background
docker compose up --build -d
```

Traces are mounted at `backend/traces/` on the host and persist between container restarts.

## Run tests

```bash
cd backend
pytest
```

## Cases

Cases live in `mock_cases/` as JSON files. Each file defines one bug scenario:

| Field | Purpose |
|-------|---------|
| `bug_signature` | The exact string present in the buggy RTL |
| `fix_replacement` | What to replace it with |
| `failure_log` / `success_log` | Simulator output for each state |
| `expected_fix_contains` | Used to score fix plausibility at 1.0 |

## Scoring

```
R_total = 0.30 × root_cause_correct
        + 0.25 × evidence_quality
        + 0.20 × tool_use_correctness
        + 0.15 × fix_plausibility
        + 0.10 × no_hallucinated_signals
        − 0.30 per forbidden_target violation
```

## Simulator adapters

`app/simulators.py` defines a `SimulatorAdapter` protocol. `MockSimulatorAdapter` is the only implementation today. A future `QuestaSimulatorAdapter` or `VCSSimulatorAdapter` would implement the same `run(case, rtl) -> SimulationResult` contract against real EDA tooling.

## Trace storage

Each `/run-case` call appends one JSON line to `traces/eval_runs.jsonl`. The file is gitignored — it is a runtime artifact, not source.
