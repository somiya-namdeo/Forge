import { request } from './apiClient';

export interface ArchitectureComparisonResult {
  comparison_id: string;
  comparison_name: string;
  winner: {
    rank: number;
    architecture_id: string;
    architecture_name: string;
    overall_score: number;
    benchmark_score: number;
    average_latency_ms: number;
    faithfulness: number;
    answer_relevancy: number;
    strengths: string[];
    weaknesses: string[];
    reason: string;
    quality_grade?: string;
    deployment_readiness?: string;
    recommendations?: string[];
  };
  runner_up?: {
    rank: number;
    architecture_id: string;
    architecture_name: string;
    overall_score: number;
    reason: string;
  } | null;
  rankings: any[];
  summary: string;
  recommendations: string[];
  metric_winners?: any[];
  trade_off_analysis?: any[];
  radar_metrics?: Record<string, Record<string, number>>;
  executive_summary?: {
    overall_winner?: string;
    overall_verdict?: string;
    best_architecture?: string;
    primary_reason?: string;
    major_tradeoff?: string;
    deployment_recommendation?: string;
    risk_analysis?: string;
  } | null;
  /** Legacy field kept for UI compatibility */
  metricComparison?: {
    metricName: string;
    valueA: string | number;
    valueB: string | number;
    winner: 'A' | 'B' | 'TIE';
    insight: string;
  }[];
  componentDiffs?: {
    category: string;
    compA: string;
    compB: string;
    tradeoffSummary: string;
  }[];
}

class ComparisonService {
  /**
   * Compare two architectures via POST /comparison/run.
   * Accepts any two architecture objects and maps them into ArchitectureCandidates.
   */
  async compareArchitectures(archA: any, archB: any): Promise<ArchitectureComparisonResult> {
    const payload = {
      comparison_name: `${archA.project_name || 'Architecture A'} vs ${archB.project_name || 'Architecture B'}`,
      optimization_goal: 'balanced',
      ranking_strategy: 'weighted_score',
      architectures: [
        {
          architecture_id: archA.id || `arch-a-${Date.now()}`,
          architecture_name: archA.project_name || 'Architecture A',
          configuration: { priority: archA.priority || 'balanced', deployment_target: archA.deployment_target || 'aws' },
          metadata: {},
        },
        {
          architecture_id: archB.id || `arch-b-${Date.now()}`,
          architecture_name: archB.project_name || 'Architecture B',
          configuration: { priority: archB.priority || 'quality', deployment_target: archB.deployment_target || 'gcp' },
          metadata: {},
        },
      ],
    };

    return request<ArchitectureComparisonResult>('/comparison/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}

export const comparisonService = new ComparisonService();
