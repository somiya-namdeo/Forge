export type Priority = 'cost' | 'quality' | 'latency' | 'balanced';
export type DecisionPriority = Priority;
export type DeploymentTarget = 'aws' | 'gcp' | 'azure' | 'on_prem' | 'local';

export interface DecisionRequest {
  project_name: string;
  project_description: string;
  expected_users?: number;
  document_count?: number;
  budget_usd?: number;
  deployment_target: DeploymentTarget;
  priority: Priority;
  preferred_llm?: string;
  constraints?: string[];
}

export interface AlternativeDetail {
  name: string;
  reason: string;
}

export interface DecisionRecommendationItem {
  category: string;
  recommended: string;
  confidence: number;
  confidence_level: string;
  reason: string;
  alternatives: string[];
  alternative_analysis: AlternativeDetail[];
  score_breakdown: Record<string, number>;
  decision_trace: string[];
  evidence: Record<string, any>;
  metadata_used: string[];
}

export interface DecisionResponse {
  id?: string;
  recommendations: DecisionRecommendationItem[];
  summary: string;
  overall_confidence: number;
  generated_at: string;
  metadata?: Record<string, string>;
  pipeline_statistics?: Record<string, any>;
}
