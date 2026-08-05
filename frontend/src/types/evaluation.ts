export interface EvaluationMetric {
  name: string;
  score: number; // 0 - 100
  target: number;
  status: 'optimal' | 'acceptable' | 'degraded';
  description: string;
}

export interface EvaluationLogItem {
  timestamp: string;
  step: string;
  status: 'info' | 'success' | 'warn';
  message: string;
}

export interface EvaluationResult {
  id: string;
  pipelineName: string;
  version: string;
  executedAt: string;
  overallHealth: 'PASSED' | 'WARNING' | 'FAILED';
  metrics: {
    faithfulness: EvaluationMetric;
    relevancy: EvaluationMetric;
    contextPrecision: EvaluationMetric;
    hallucinationIndex: EvaluationMetric;
    latencyP95: EvaluationMetric;
  };
  testLogs: EvaluationLogItem[];
  sampleEvaluations: {
    query: string;
    retrievedDocs: number;
    faithfulnessScore: number;
    hallucinationDetected: boolean;
  }[];
}
