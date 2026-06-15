export interface IngestResponse {
  case: DVCase;
  inferred_fields: string[];
}

export interface DVCase {
  id: string;
  title: string;
  description: string;
  rtl: string;
  testbench: string;
  expected_root_cause: string;
  valid_signals: string[];
  forbidden_targets: string[];
  bug_signature: string;
  fix_replacement: string;
  failure_log: string;
  success_log: string;
  failure_coverage: number;
  success_coverage: number;
  expected_fix_contains?: string;
}

export interface AgentAction {
  step: number;
  tool_name: string;
  input: string;
  output: string;
}

export interface EvaluationScores {
  root_cause_correct: number | null; // null in Analysis mode (no ground truth)
  evidence_quality: number;
  tool_use_correctness: number;
  fix_plausibility: number;
  no_hallucinated_signals: number;
}

export interface Trajectory {
  case_id: string;
  root_cause: string;
  proposed_fix: string;
  actions: AgentAction[];
  evidence: string[];
  scores: EvaluationScores;
  penalties: string[];
  constitutional_violations: string[];
  r_total: number;
  eval_mode: boolean; // false = Analysis mode, agent output is the diagnosis
}
