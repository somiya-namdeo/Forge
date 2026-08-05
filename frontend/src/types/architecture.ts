export interface ArchitectureComponent {
  id: string;
  category: 'LLM' | 'EMBEDDING' | 'VECTOR_DB' | 'RETRIEVER' | 'CHUNKING' | 'FRAMEWORK' | 'RERANKER' | 'GATEWAY';
  name: string;
  score: number;
  confidence: number; // 0-100
  latency: string;
  cost: string;
  complexity: 'Low' | 'Medium' | 'High';
  tags: string[];
  justification?: string;
  rejectionAnalysis?: { rejectedModel: string; reason: string }[];
  evidence?: { benchmarkName: string; result: string };
}

export interface ArchitectureSummary {
  overallScore: number; // e.g. 94
  productionReadiness: 'Production Ready' | 'Review Required' | 'Experimental';
  estimatedMonthlyCost: string; // e.g. "$420 / mo"
  estimatedLatency: string; // e.g. "~140ms (p95)"
  complexity: 'Low' | 'Medium' | 'High' | 'Enterprise-Grade';
  scalability: string; // e.g. "Up to 50M vectors"
  reasoningConfidence: string; // e.g. "96.4% High"
  deploymentDifficulty: 'Turnkey' | 'Moderate' | 'Complex / Custom VPC';
}

export interface DiagramNode {
  id: string;
  title: string;
  subtitle: string;
  category: string;
}

export interface GeneratedArchitecture {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  summary: ArchitectureSummary;
  components: ArchitectureComponent[];
  diagramNodes: DiagramNode[];
}
