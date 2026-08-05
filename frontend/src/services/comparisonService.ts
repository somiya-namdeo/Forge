import { simulateLatency } from './apiClient';
import { GeneratedArchitecture } from '../types';

export interface ArchitectureComparisonResult {
  archA: GeneratedArchitecture;
  archB: GeneratedArchitecture;
  metricComparison: {
    metricName: string;
    valueA: string | number;
    valueB: string | number;
    winner: 'A' | 'B' | 'TIE';
    insight: string;
  }[];
  componentDiffs: {
    category: string;
    compA: string;
    compB: string;
    tradeoffSummary: string;
  }[];
}

class ComparisonService {
  async compareArchitectures(archA: GeneratedArchitecture, archB: GeneratedArchitecture): Promise<ArchitectureComparisonResult> {
    await simulateLatency(800);

    return {
      archA,
      archB,
      metricComparison: [
        {
          metricName: 'Overall Engineering Score',
          valueA: archA.summary.overallScore,
          valueB: archB.summary.overallScore,
          winner: archA.summary.overallScore >= archB.summary.overallScore ? 'A' : 'B',
          insight: 'Reflects composite weighting across accuracy, latency, infrastructure reliability, and financial scale.'
        },
        {
          metricName: 'Estimated Monthly Cost',
          valueA: archA.summary.estimatedMonthlyCost,
          valueB: archB.summary.estimatedMonthlyCost,
          winner: 'A',
          insight: 'Open weights and self-hosted Rust vector indexes reduce recurring token API overhead significantly.'
        },
        {
          metricName: 'End-to-End Latency (p95)',
          valueA: archA.summary.estimatedLatency,
          valueB: archB.summary.estimatedLatency,
          winner: 'A',
          insight: 'Eliminating external network hops between cloud retrieval endpoints cuts overall roundtrip delay.'
        },
        {
          metricName: 'Reasoning Confidence',
          valueA: archA.summary.reasoningConfidence,
          valueB: archB.summary.reasoningConfidence,
          winner: 'TIE',
          insight: 'Both architectures meet strict regulatory faithfulness thresholds (>90% evaluation target).'
        }
      ],
      componentDiffs: [
        {
          category: 'LLM Engine',
          compA: 'Llama 3.3 70B (vLLM / Groq)',
          compB: 'OpenAI GPT-4o / Claude 3.5 Sonnet',
          tradeoffSummary: 'Open weights provide complete data governance and cost predictability; proprietary models offer slightly higher zero-shot edge domain handling.'
        },
        {
          category: 'Vector DB & Search',
          compA: 'Qdrant Enterprise (Rust)',
          compB: 'Pinecone Serverless / Managed Cloud',
          tradeoffSummary: 'Qdrant delivers superior HNSW filtering speed and local memory footprint; Pinecone offers turnkey multi-region serverless auto-scaling.'
        },
        {
          category: 'Retrieval Layer',
          compA: 'Hybrid (BM25 + Dense + BGE Reranker)',
          compB: 'Dense Vector-Only Retrieval',
          tradeoffSummary: 'Hybrid retrieval guarantees lexical matching on acronyms and exact serial numbers at the cost of slight compute indexing complexity.'
        }
      ]
    };
  }
}

export const comparisonService = new ComparisonService();
