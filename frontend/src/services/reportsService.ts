import { simulateLatency } from './apiClient';
import { ArchitectureReport, GeneratedArchitecture } from '../types';

class ReportsService {
  async generateReport(arch: GeneratedArchitecture): Promise<ArchitectureReport> {
    await simulateLatency(600);

    return {
      id: `rep-${Date.now()}`,
      title: `${arch.title} — Production Engineering Summary`,
      generatedAt: new Date().toLocaleString(),
      architecture: arch,
      deploymentChecklist: [
        {
          id: 'chk-1',
          category: 'Infrastructure',
          task: 'Configure GPU inference nodes or low-latency endpoint connection (vLLM / Groq API keys)',
          description: 'Ensure TLS 1.3 encryption and VPC peering for private inference throughput.',
          completed: true,
          criticality: 'Required'
        },
        {
          id: 'chk-2',
          category: 'Vector DB & Search',
          task: 'Initialize Qdrant HNSW collection with payload index schemas',
          description: 'Set distance metric to Cosine and enable on-disk payload storage for memory optimization.',
          completed: true,
          criticality: 'Required'
        },
        {
          id: 'chk-3',
          category: 'Security',
          task: 'Enforce Kong API Gateway rate-limiting policies and JWT verification',
          description: 'Prevent token DDoS attacks and enforce per-user budget allocation throttles.',
          completed: false,
          criticality: 'Required'
        },
        {
          id: 'chk-4',
          category: 'Monitoring',
          task: 'Connect LangSmith / OpenTelemetry traces to evaluation dashboard',
          description: 'Capture live faithfulness metrics and automatically flag hallucination drift above 5%.',
          completed: false,
          criticality: 'Recommended'
        }
      ],
      costBreakdown: [
        { item: 'LLM Inference (70B Instruct Token Volume)', monthlyCostUsd: 210, share: 55 },
        { item: 'Qdrant Vector Database Cluster (Managed VPC)', monthlyCostUsd: 95, share: 25 },
        { item: 'Embedding & Reranker Local Compute Nodes', monthlyCostUsd: 50, share: 13 },
        { item: 'Kong API Gateway & Telemetry Buffer', monthlyCostUsd: 30, share: 7 }
      ],
      productionReadinessSummary: {
        ready: true,
        passCount: 14,
        warnCount: 1,
        riskSummary: 'Pipeline meets all latency (p95 < 200ms) and faithfulness (Score > 90) criteria for production deployment.'
      }
    };
  }

  async exportReportAsJson(report: ArchitectureReport): Promise<string> {
    await simulateLatency(300);
    return JSON.stringify(report, null, 2);
  }

  async triggerPrintablePdf(reportTitle: string): Promise<void> {
    await simulateLatency(400);
    console.log(`[Reports Service] Triggered production PDF compilation for: ${reportTitle}`);
    // In real browser context, this triggers window.print() or generates blob download
    if (typeof window !== 'undefined') {
      window.print();
    }
  }
}

export const reportsService = new ReportsService();
