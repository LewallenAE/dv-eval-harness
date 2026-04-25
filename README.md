# Design Verification Evaluation Harness

I intentionally did not depend on proprietary EDA tools for the prototype. I built a simulator adapter boundary. The current implementation uses a deterministic mock simulator, but the agent runner, evaluator, trace store, and reward pipeline consume a stable simulation result interface. Replacing the mock with Questa or VCS is an adapter implementation, not a system rewrite.


