export interface BenchmarkRunConfig {
  dataset: string;
  architectures: string[];
  metrics: string[];
  concurrency?: number;
}

export interface BenchmarkLeaderboardEntry {
  rank: number;
  architectureName: string;
  llmModel: string;
  vectorDb: string;
  latencyP50: number; // in ms
  latencyP95: number;
  latencyP99: number;
  throughputTokSec: number;
  accuracyScore: number; // 0 - 100
  costPerMillionTokens: number; // USD
  status: 'Verified' | 'Beta' | 'Unverified';
}

export interface BenchmarkReport {
  id: string;
  testName: string;
  dataset: string;
  executedAt: string;
  durationSeconds: number;
  totalQueriesProcessed: number;
  leaderboard: BenchmarkLeaderboardEntry[];
  summaryInsights: string[];
}
