# dv-eval-harness

**The Sovereign Silicon Intelligence Engine**  
*Bridging Large Language Models and Hardware Verification*

A vertically integrated evaluation framework that turns raw RTL and simulation logs into structured **Agentic Trajectories**, scored by a deterministic reward model and formatted for **Direct Preference Optimization (DPO)**.

> “If the code doesn’t compile on the metal, the intelligence doesn’t exist.”

## Project Pillars

- **Deterministic Rigor** — 100% Pydantic-enforced schemas with strict field ordering for predictable, “no-surprises” behavior.
- **The Trinity of Simulation** — A unified adapter supporting Mock (fast iteration), Icarus Verilog (real metal), and Cocotb + pyuvm (Python-native hardware verification).
- **Hardware-Aware Rewards** — A multi-objective scalar reward (`R_total`) that penalizes hallucinated signals and rewards functional coverage and correct root cause identification.
- **Direct Preference Optimization (DPO) Ready** — Automatic generation of (chosen/rejected) preference pairs for training LLMs to reason about temporal logic, protocols, and hardware bugs.

## Tech Stack

| Component       | Technology                  | Role                              |
|-----------------|-----------------------------|-----------------------------------|
| Orchestrator    | Python 3.12+ / FastAPI      | The nervous system                |
| Package Manager | uv                          | High-speed dependency management  |
| Logic Engine    | Pydantic v2                 | Structural integrity & validation |
| Physics (Metal) | Icarus Verilog              | Binary RTL compilation            |
| Neural Bridge   | Cocotb + pyuvm              | Pythonic hardware verification    |
| Optimization    | PyTorch (DPO)               | Preference learning logic         |

## The Agentic Loop: Silicon → Synapse

For every hardware case, the harness executes this 5-step trajectory:

1. **Baseline** — Run simulation on broken RTL to capture the failure signature.
2. **Analysis** — Filter logs for critical tokens (UVM_ERROR, ASSERTION FAILED, FATAL).
3. **Inspection** — Scan RTL for configured bug signatures (FSM, protocol, buffer, etc.).
4. **Proposal** — The agent proposes a logical fix.
5. **Verification** — Re-run simulation to measure coverage delta and final reward.

## The Deterministic “Math Teacher” Reward Model

We evaluate every trajectory with a weighted scalar reward:

**R_total** = *w_rc*·R_root_cause + *w_eq*·R_evidence + *w_tu*·R_tool_use + *w_fp*·R_fix_plausibility + *w_nh*·R_no_hallucination − Penalties

Penalties are applied instantly for modifying forbidden targets (scoreboards, monitors, testbenches, etc.).

## Installation

**Binary Requirements (Linux/WSL):**

```bash
sudo apt update && sudo apt install iverilog -yv
```

## Python Environment:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Quick Start:

```bash
uv run smoke_test.py
```

### Expected Output:

```text
🚀 Launching Sovereign Verification Suite...
AXI valid drops before ready...     R_Total: 0.93  ✓
FSM stuck in IDLE...                R_Total: 0.93  ✓
UART FIFO overflow write...         R_Total: 0.93  ✓

✅ Suite complete. Results saved to smoke_test_results.json
```

## Roadmap
- Supabase integration for live trajectory leaderboard
- Next.js dashboard for agent performance visualization
- Large-scale DPO dataset generation for fine-tuning
- Production Questa and VCS adapters


**Developed by Anthony Eugene Lewallen**  
<sub>End-to-End AI Systems Engineer [Model Internals -> MLOps + Agentic Systems]</sub>  
<sub>From the Metal to the Agent Level</sub>


B.S. Mathematics Operations Research (Summa Cum Laude) - American Public University  
MAS-CS (Software Systems) + MSE-AI - University of Pennsylvania

