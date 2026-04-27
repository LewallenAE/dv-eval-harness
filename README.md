# dv-eval-harness

Evaluation harness for LLM-based design verification agents. Generates scored trajectories against broken RTL, decomposes reward across five components, emits DPO-ready preference pairs.

## What it does

Given a buggy RTL module and a known root cause, the harness drives an agent through a 5-step debug trajectory, scores the trajectory deterministically, and persists the trace as JSONL. Trajectories with chosen/rejected pairs become DPO training data.

The simulator boundary is an adapter. Mock for fast iteration, Icarus for free metal, Cocotb+pyuvm for Python-native UVM. Questa and VCS slot in behind the same interface.

## Why the design looks like this

**Adapter at the simulator boundary.** The DV simulator landscape is fragmented (Icarus, Verilator, Questa, VCS, Xcelium). Hardcoding any one couples the harness to a vendor and breaks portability across customer environments. Same trajectory runs against any backend.

**Discriminated unions on bug family.** Cases are typed by family (FIFO, FSM, arbiter, AXI-Lite). Each subclass enforces family-specific fields at ingestion — FIFO cases require pointer width, FSM cases require state enum and encoding, arbiters require sticky semantics, AXI-Lite requires channel and violation type. Pydantic v2 routes by the `family` field. Invalid cases fail at load, not at runtime.

**Reward decomposition over scalar.** A scalar reward hides what the agent did right or wrong. The harness emits five components — root cause, evidence quality, tool use correctness, fix plausibility, no-hallucination — plus a per-step PRM mean folded into the total. Decomposed rewards are diagnostic; scalar rewards are debug-hostile.

**Categorical penalties for bright-line violations only.** Modifying forbidden targets (scoreboards, monitors, testbenches) triggers a fixed scalar penalty. Fuzzy gaming detection is not handled in the reward function — it belongs in the trajectory audit layer where the agent can't optimize against it.

**JSONL trace persistence.** Append-only, grep-able, replayable. No ORM ceremony for what is fundamentally a log.

## The trajectory

For each case the agent executes:

1. Baseline simulation on broken RTL — capture the failure signature
2. Log analysis — filter for UVM_ERROR, ASSERTION FAILED, FATAL
3. RTL inspection — scan for configured bug signatures
4. Fix proposal
5. Re-run — measure coverage delta and final reward

## Reward

```
R_total = w_rc·R_root_cause
        + w_eq·R_evidence
        + w_pr·R_prm_mean
        + w_fp·R_fix_plausibility
        + w_tu·R_tool_use
        − Σ penalties
```

Weights sum to 1.0, asserted at module load. Penalties fire on protocol-level violations. PRM mean injects per-step process reward so trajectory-level scoring is sensitive to reasoning quality, not just final outcome.

## Dataset

200 cases across four bug families, generated from hand-authored blueprints against the discriminated union schemas. Each case validates end-to-end through the harness before inclusion. Families cover the four primitives of digital design — storage, protocol, sequential, concurrent.

| Family            | Cases | Tests |
|-------------------|-------|-------|
| FIFO buffers      | 50    | Pointer arithmetic, full/empty flag races, overflow/underflow |
| AXI-Lite          | 50    | Handshake (valid/ready ordering), address phase, response codes |
| FSM controllers   | 50    | Transitions, stuck states, encoding width, default-case latches |
| Round-robin       | 50    | Fairness, sticky grants, last-granted rotation |

Each case generates one DPO preference pair (chosen fix vs rejected fix). 200 pairs is the floor for QLoRA + DPO on a 7B base — enough to measurably shift behavior without overfitting to a single bug class.

## Stack

| Layer                | Choice               | Why |
|----------------------|----------------------|-----|
| Orchestrator         | Python 3.12 + FastAPI| Async, boring, fast to ship |
| Packaging            | uv                   | Fast resolves, lockfile reproducibility |
| Schemas              | Pydantic v2          | Discriminated unions, strict validation |
| Sim (free)           | Icarus Verilog       | Real metal, no license |
| Sim (Python)         | Cocotb + pyuvm       | Pythonic UVM, integrates directly |
| Preference learning  | PyTorch (DPO)        | Offline, no reward model to train, no rollouts |

## Install

```
sudo apt update && sudo apt install iverilog -y
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
```

## Run

```
uv run smoke_test.py
```

Expected:

```
AXI valid drops before ready...     R_Total: 0.93  ok
FSM stuck in IDLE...                R_Total: 0.93  ok
UART FIFO overflow write...         R_Total: 0.93  ok

Suite complete. Results saved to smoke_test_results.json
```

## What's working

- Adapter boundary with Mock + Icarus paths
- Discriminated union schemas for FIFO / FSM / arbiter / AXI-Lite cases
- Reward engine: 5-component decomposition + PRM mean injection, weight invariant asserted at load, regex word-boundary substring matching, clamped at zero
- Trajectory persistence as JSONL
- Reward engine test suite (weight invariant, word-boundary regression, PRM stacking, R_total clamp, tool-use validity ratio)

## What's next

- Cocotb + pyuvm adapter (in progress)
- Family-level design pattern schemas for structural conformance checks beyond functional simulation (canonical FIFO/FSM/arbiter shape validation)
- Trajectory audit layer for forensic gaming detection (CoT-action coherence, fix-before-evidence, hallucinated citations, conditional-independence violations)
- Held-out reward function R₂ for threshold-hugging detection (R₁/R₂ gap as an independent telemetry channel)
- QLoRA + DPO fine-tune on Mistral 7B / Llama 3 8B against harness-generated preference data
- Questa and VCS adapters
- Supabase persistence + Next.js dashboard for trajectory leaderboard
- Programmatic bug injection to scale beyond 200 hand-blueprinted cases

## Status

Built as a focused demonstration of the eval harness layer for DV agents. Architecture decisions are deliberate; coverage is intentionally narrow (four bug families) to ship a working end-to-end loop before scaling cases. The roadmap items are not vaporware — each one names a specific failure mode in the current implementation that the upgrade addresses.

---

**Anthony Eugene Lewallen**
End-to-End AI Systems Engineer · Model Internals → MLOps + Agentic Systems
*From the Metal to the Agent Level*

B.S. Mathematics Operations Research, Summa Cum Laude — American Public University  
MAS-CS (Software Systems) + MSE-AI — University of Pennsylvania    
  
  
6,000+ hours RLHF · adversarial evaluation @ Snorkel AI · top-tier @ Alignerr