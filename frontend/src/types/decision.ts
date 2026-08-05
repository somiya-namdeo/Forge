export type Priority = 'cost' | 'quality' | 'latency' | 'balanced';
/** Alias used by pages that import DecisionPriority */
export type DecisionPriority = Priority;
export type DeploymentTarget = 'aws' | 'gcp' | 'azure' | 'on_prem' | 'on-prem' | 'local';

export interface DecisionRequest {
  projectName: string;
  projectDescription: string;
  expectedUsers?: number;
  documentCount?: number;
  budgetUsd?: number;
  deploymentTarget: DeploymentTarget;
  priority: Priority;
  preferredLlm?: string;
  constraints?: string[];
}

export interface AlternativeDetail {
  name: string;
  reason: string;
  scorePenalty: string;
}

export interface DecisionRecommendationItem {
  category: string;
  recommended: string;
  confidence: number; // 0 - 100
  confidenceLevel: 'Very High' | 'High' | 'Medium' | 'Low';
  reason: string;
  alternatives: string[];
  alternativeAnalysis: AlternativeDetail[];
  scoreBreakdown: { [key: string]: number };
  decisionTrace: string[];
  benchmarkEvidence: { metric: string; score: string; comparison: string };
  costVsPerformance: { costIndex: number; perfIndex: number; note: string };
  latencyVsAccuracy: { latencyMs: number; accuracyPct: number; note: string };
}

export interface DecisionResponse {
  id: string;
  recommendations: DecisionRecommendationItem[];
  summary: string;
  overallConfidence: number;
  generatedAt: string;
  pipelineStatistics: { durationMs: number; evaluatedCandidates: number };
}
