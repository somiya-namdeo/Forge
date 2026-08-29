/** Maps to backend BenchmarkSample model */
export interface BenchmarkSample {
  sample_id?: string;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard';
  question: string;
  contexts?: string[];
  ground_truth?: string;
  expected_answer?: string;
}

/** Maps to backend BenchmarkRunConfig model */
export interface BenchmarkRunConfig {
  benchmark_name?: string;
  rag_architecture_id?: string;
  dataset_id?: string;
  samples?: BenchmarkSample[];
  provider?: 'ragas' | 'deepeval' | 'custom' | 'deterministic';
  weight_preset?: string;
  async_execution?: boolean;
  parallel_workers?: number;
  shuffle?: boolean;
  max_samples?: number;
  /** @deprecated Use BenchmarkRunConfig.samples instead */
  dataset?: string;
  /** @deprecated Not used by backend */
  architectures?: string[];
  /** @deprecated Not used by backend */
  metrics?: string[];
  /** @deprecated Not used by backend */
  concurrency?: number;
  metric_config?: { metric_type: string; provider: string; weight: number }[];
}

export interface BenchmarkMetricStatistics {
  average: number;
  median: number;
  minimum: number;
  maximum: number;
  standard_deviation: number;
}

export interface BenchmarkStatistics {
  total_samples: number;
  passed_samples: number;
  failed_samples: number;
  warning_samples?: number;
  average_score: number;
  median_score: number;
  minimum_score: number;
  maximum_score: number;
  score_standard_deviation: number;
  average_execution_time_ms: number;
  p95_execution_time_ms: number;
  success_rate: number;
  failure_rate: number;
  metric_averages?: Record<string, number>;
  metric_statistics?: Record<string, BenchmarkMetricStatistics>;
  generation_metric_averages?: Record<string, number>;
  retrieval_metric_averages?: Record<string, number>;
  top_strengths?: string[];
  top_weaknesses?: string[];
  top_recommendations?: string[];
}

export interface BenchmarkExecutiveSummary {
  overall_verdict?: string;
  best_metric?: string;
  weakest_metric?: string;
  primary_bottleneck?: string;
  recommended_next_action?: string;
}

/** Maps to backend BenchmarkReport model */
export interface BenchmarkReport {
  benchmark_name: string;
  benchmark_version?: string;
  provider: string;
  started_at: string;
  completed_at: string;
  statistics: BenchmarkStatistics;
  results: any[];
  quality_grade?: string;
  deployment_readiness?: string;
  overall_strengths?: string[];
  overall_weaknesses?: string[];
  overall_recommendations?: string[];
  executive_summary?: BenchmarkExecutiveSummary;
  metadata?: Record<string, any>;
  /** @deprecated legacy frontend-only fields kept for UI compatibility */
  id?: string;
  testName?: string;
  dataset?: string;
  executedAt?: string;
  durationSeconds?: number;
  totalQueriesProcessed?: number;
  leaderboard?: any[];
  summaryInsights?: string[];
}

/** Legacy leaderboard type kept for display compatibility */
export interface BenchmarkLeaderboardEntry {
  rank: number;
  architectureName: string;
  llmModel: string;
  vectorDb: string;
  latencyP50: number;
  latencyP95: number;
  latencyP99: number;
  throughputTokSec: number;
  accuracyScore: number;
  precision: number;
  recall: number;
  passRate: number;
  costPerMillionTokens: number;
  status: 'Verified' | 'Beta' | 'Unverified' | 'Not Yet Benchmarked';
}
