export interface MetricResult {
  name: string;
  score: number | string;
  target: number;
  status: 'optimal' | 'warning' | 'critical';
  description: string;
}

export interface EvaluationResult {
  evaluation_id: string;
  evaluation_version: string;
  provider: string;
  overall_score: number;
  quality_grade: string;
  deployment_readiness: string;
  status: 'PASS' | 'FAIL' | 'WARNING';
  summary: {
    overall_score: number;
    status: string;
    strengths: string[];
    weaknesses: string[];
    recommendations: string[];
  };
  retrieval: {
    precision_at_k: number;
    recall_at_k: number;
    hit_rate: number;
    mrr: number;
    ndcg: number;
  };
  generation: {
    faithfulness: number;
    answer_relevancy: number;
  };
  operational: {
    retrieval_latency_ms: number;
    generation_latency_ms: number;
    total_latency_ms: number;
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    estimated_cost_usd: number;
    throughput_tokens_per_second: number;
  };
  created_at: string;
  
  // Keep legacy fields so UI doesn't crash before being refactored
  id?: string;
  pipelineName?: string;
  version?: string;
  executedAt?: string;
  overallHealth?: string;
  metrics?: Record<string, MetricResult>;
  testLogs?: Array<{ timestamp: string; step: string; status: 'info' | 'success' | 'error' | 'warning'; message: string }>;
  sampleEvaluations?: Array<{ query: string; retrievedDocs: number; faithfulnessScore: number; hallucinationDetected: boolean }>;
}
