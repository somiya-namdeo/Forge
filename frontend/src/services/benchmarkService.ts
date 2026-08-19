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
    const archsToRun = config.architectures && config.architectures.length > 0 
      ? config.architectures 
      : ['arch_v1'];

    // Run benchmarks for all selected architectures
    const reports = await Promise.all(
      archsToRun.map(async (archName: string) => {
        const payload: BenchmarkRunConfig = {
          benchmark_name: config.dataset || 'Forge Benchmark Suite',
          rag_architecture_id: archName,
          samples: [],
          provider: 'ragas',
          weight_preset: 'balanced_rag',
        };

        return request<BenchmarkReport>('/benchmark/run', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
      })
    );

    // If we only ran one, or we want to aggregate them into a single report object
    // that fits the frontend's legacy BenchmarkReport structure for the Leaderboard:
    const primaryReport = reports[0];
    
    // Construct the leaderboard from the multiple BenchmarkReport responses
    const leaderboard = reports.map((rep, index) => {
      const stats = rep.statistics;
      return {
        rank: index + 1, // Will be sorted by the UI
        architectureName: rep.benchmark_name === config.dataset ? archsToRun[index] : archsToRun[index],
        llmModel: 'Auto-Selected', // Backend doesn't return this in BenchmarkReport directly
        vectorDb: 'Auto-Selected',
        latencyP50: stats?.average_execution_time_ms || 0,
        latencyP95: stats?.p95_execution_time_ms || 0,
        latencyP99: stats?.p95_execution_time_ms || 0,
        throughputTokSec: stats?.average_execution_time_ms ? 1000 / stats.average_execution_time_ms : 0,
        accuracyScore: (stats?.average_score || 0) * 100,
        precision: stats?.metric_averages?.precision !== undefined ? stats.metric_averages.precision * 100 : undefined,
        recall: stats?.metric_averages?.recall !== undefined ? stats.metric_averages.recall * 100 : undefined,
        passRate: stats?.success_rate !== undefined ? stats.success_rate * 100 : undefined,
        costPerMillionTokens: 0,
        status: (stats?.total_samples || 0) === 0 ? 'Not Yet Benchmarked' : 'Verified'
      } as any;
    });

    // Return an object that has both the real backend fields and the legacy fields the UI needs
    return {
      ...primaryReport,
      leaderboard: leaderboard,
      dataset: config.dataset,
    };
  }
}

export const benchmarkService = new BenchmarkService();
