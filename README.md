# ⚡ DV-EVAL-HARNESS

## The Sovereign Silicon Intelligence Engine

### DV-Eval-Harness is a vertically integrated evaluation framework designed to bridge the gap between Large Language Models and Hardware Verification (DV). It transforms raw RTL and simulation logs into structured Agentic Trajectories, graded by a deterministic "Math Teacher" reward model, and formatted for Direct Preference Optimization (DPO).

| | "If the code doesn't compile on the metal, the intelligence doesn't exist." | |

## 🏛️ Project Pillars

- Deterministic Rigor: 100% Pydantic-enforced schemas with strict alphabetical field ordering for predictable serialization and "No-Surprises" architecture.
- The Trinity of Simulation: A unified adapter interface supporting Mock (Development), Icarus Verilog (Metal), and Cocotb/pyuvm (Neural Bridge).
- Hardware-Aware Rewards: A multi-objective scalar reward function ($R_{total}$) that penalizes "hallucinated signals" and rewards functional coverage.
- RLHF Ready: Automated generation of $(y_w, y_l)$ preference pairs for training LLMs to reason about temporal logic and protocol handshakes.

  

## 🛠️ The Tech Stack

| Component |	Technology | Role |
| :---------: | :----------: | :----: |
| Orchestrator	| Python 3.12+ / FastAPI |	The Nervous System |
| Package Manager |	uv | High-speed dependency isolation |
| Logic Engine |	Pydantic V2 |	Structural Integrity & Validation |
| Physics (Metal) |	Icarus Verilog	| Binary RTL Compilation |
| Neural Bridge |	Cocotb / pyuvm |	Pythonic Hardware Verification |
| Optimization |	PyTorch (DPO)	| Preference Learning Logic |

## 🚀 The Agentic Loop: "Silicon-to-Synapse"
The harness executes a 5-step trajectory for every hardware case:

1. Baseline: Run simulator on broken RTL to capture the failure signature.

2. Analysis: Filter logs for UVM_ERROR, ASSERTION FAILED, and FATAL tokens.

3. Inspection: Scan RTL for configured bug signatures (Protocol, FSM, or Buffer).

4. Proposal: The Agent (or LLM) proposes a logical fix.

5. Verification: Re-run simulation to calculate the final Delta-Coverage and Reward.


## 📊 The "Math Teacher" Reward Model

We evaluate agents using a scalarized objective function:
$$R_{total} = w_{rc}R_{rc} + w_{eq}R_{eq} + w_{tu}R_{tu} + w_{fp}R_{fp} + w_{nh}R_{nh} - \sum Penalties$$$R_{rc}$ 
- (Root Cause): Did the agent identify the actual bug?
- $R_{fp}$ (Fix Plausibility): Does the fix follow Verilog best practices (e.g., Non-blocking assignments)?
- Penalties: Instant deductions for modifying "Forbidden Targets" like scoreboards, monitors, or testbenches.


## 📥 Installation
Ensure you have the "Binary Requirements" installed in your WSL/Linux environment:

Bash
# Install the Metal (Icarus Verilog)
sudo apt update && sudo apt install iverilog -y

# Install the Python Nervous System
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

## 🧪 Quick Start: The Smoke Test
To verify the harness is firing on all cylinders across AXI, FSM, and UART failure modes:

Bash
uv run smoke_test.py

### Expected Output
🚀 [START] Launching Sovereign Verification Suite...

Processing: AXI valid drops before ready...  | R_Total: 0.93 | Correct: True
Processing: FSM stuck in IDLE...             | R_Total: 0.93 | Correct: True
Processing: UART FIFO overflow write...      | R_Total: 0.93 | Correct: True

✅ HURRAY! Suite complete. Results saved to smoke_test_results.json

## 🗺️ Roadmap
1. [ ] Supabase Handshake: Live persistence of trajectories to a cloud leaderboard.

2. [ ] Next.js Dashboard: A "TADA" visualization of agent performance over time.

3. [ ] DPO Dataset Batching: Exporting 1000+ pairs for fine-tuning "Sovereign-1" models.

Developed in the Code Cave by Anthony Eugene Lewallen. 

- B.S.c Mathematics Operations Research Summa Cum Laude @ American Public University
- MAS-CS Concentration in Software Systems / MSE-AI @ University of Pennsylvania
