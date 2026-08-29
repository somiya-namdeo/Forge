import { request } from './apiClient';
import { BenchmarkRunConfig, BenchmarkReport } from '../types';

class BenchmarkService {
  async getLatestReport(): Promise<BenchmarkReport | null> {
    throw new Error('Backend Not Available');
  }

  /**
   * Execute benchmark suite via POST /benchmark/run against the FastAPI backend.
   * To support the frontend's multi-architecture leaderboard UI, if multiple architectures
   * are provided, this will run them sequentially or in parallel and aggregate the results.
   */
  async runBenchmark(config: any): Promise<any> {
    
    const metricMapping: Record<string, string> = {
      'Faithfulness': 'faithfulness',
      'Relevancy': 'answer_relevance',
      'Latency': 'latency',
      'Cost': 'cost'
    };

    const archsToRun = config.architectures && config.architectures.length > 0 
      ? config.architectures 
      : ['arch_v1'];

    const reports = [];
    for (const archName of archsToRun) {
      const payload: BenchmarkRunConfig = {
        benchmark_name: config.dataset || 'Forge Benchmark Suite',
        rag_architecture_id: archName,
        samples: [],
        provider: 'ragas',
        weight_preset: 'balanced_rag',
        metric_config: config.metrics ? config.metrics.map((m: string) => ({ metric_type: metricMapping[m] || 'custom', provider: 'ragas', weight: 1.0 })) : undefined,
      };

      try {
        const res = await request<BenchmarkReport>('/benchmark/run', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        reports.push({ success: true, archName, data: res });
      } catch (err: any) {
        reports.push({ success: false, archName, error: err.message || 'Benchmark failed' });
      }
    }

    // Pick a primary report for the baseline structure if one succeeded
    const successfulReports = reports.filter(r => r.success);
    let primaryReport = successfulReports.length > 0 ? successfulReports[0].data : null;
    
    // Construct the leaderboard
    const leaderboard = reports.map((rep, index) => {
      if (!rep.success || !rep.data) {
         return {
            rank: index + 1,
            architectureName: rep.archName,
            llmModel: '-',
            vectorDb: '-',
            latencyP50: null,
            latencyP95: null,
            latencyP99: null,
            throughputTokSec: null,
            accuracyScore: null,
            precision: null,
            recall: null,
            passRate: null,
            costPerMillionTokens: null,
            status: 'Failed',
            reason: rep.error
         };
      }
      const stats = rep.data.statistics;
      const isUnbenchmarked = (stats?.total_samples || 0) === 0;
      return {
        rank: index + 1, // Will be sorted by the UI
        architectureName: rep.archName,
        llmModel: 'Auto-Selected',
        vectorDb: 'Auto-Selected',
        latencyP50: isUnbenchmarked ? null : stats?.average_execution_time_ms || 0,
        latencyP95: isUnbenchmarked ? null : stats?.p95_execution_time_ms || 0,
        latencyP99: isUnbenchmarked ? null : stats?.p95_execution_time_ms || 0,
        throughputTokSec: isUnbenchmarked ? null : (stats?.average_execution_time_ms ? 1000 / stats.average_execution_time_ms : 0),
        accuracyScore: isUnbenchmarked ? null : (stats?.average_score || 0) * 100,
        precision: isUnbenchmarked ? null : (stats?.metric_averages?.precision_at_k !== undefined ? stats.metric_averages.precision_at_k * 100 : null),
        recall: isUnbenchmarked ? null : (stats?.metric_averages?.recall_at_k !== undefined ? stats.metric_averages.recall_at_k * 100 : null),
        passRate: isUnbenchmarked ? null : (stats?.success_rate !== undefined ? stats.success_rate * 100 : null),
        costPerMillionTokens: isUnbenchmarked ? null : 0,
        status: isUnbenchmarked ? 'Not Yet Benchmarked' : 'Verified'
      } as any;
    });

    if (!primaryReport) {
       // if all failed
       primaryReport = {
         benchmark_name: config.dataset,
         results: [],
         provider: 'ragas',
         started_at: '',
         completed_at: '',
         statistics: {
            total_samples: 0,
            passed_samples: 0,
            failed_samples: 0,
            average_score: 0,
            median_score: 0,
            minimum_score: 0,
            maximum_score: 0,
            score_standard_deviation: 0,
            average_execution_time_ms: 0,
            p95_execution_time_ms: 0,
            success_rate: 0,
            failure_rate: 0
         }
       };
    }

    // Return an object that has both the real backend fields and the legacy fields the UI needs
    return {
      ...primaryReport,
      all_reports: reports,
      leaderboard: leaderboard,
      dataset: config.dataset,
    };
  }
}

export const benchmarkService = new BenchmarkService();
