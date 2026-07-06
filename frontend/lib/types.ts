// Mirrors backend/app/models/schemas.py — keep in sync with the API contract.

export interface AgentResult {
  role: string;
  analysis: string;
  confidence: number;
  objections: string[];
  recommendation: string;
}

export interface DebateTimelineEntry {
  step: number;
  role: string;
  message: string;
  responding_to: string | null;
}

export interface ConsensusExplanation {
  supporting_arguments: string[];
  main_objections: string[];
  reasoning: string;
}

export type AgreementLevel =
  | "Strong Consensus"
  | "Moderate Consensus"
  | "Weak Consensus"
  | "Highly Contested";

export interface ConsensusSummary {
  final_recommendation: string;
  overall_confidence: number;
  agreement_level: AgreementLevel;
  key_risks: string[];
  key_objections: string[];
  dissenting_roles: string[];
  explanation: ConsensusExplanation;
}

export type MetricLevel = "Low" | "Medium" | "High";

export interface CouncilMetrics {
  council_confidence: number;
  agreement_score: number;
  risk_level: MetricLevel;
  evidence_quality: MetricLevel;
}

export interface DeliberateResponse {
  problem: string;
  agents: AgentResult[];
  timeline: DebateTimelineEntry[];
  consensus: ConsensusSummary;
  metrics: CouncilMetrics;
  timestamp: string;
  protocol_version: string;
}
