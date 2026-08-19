export interface ProjectInfo {
  project_name: string;
  domain: string;
  scale: string;
  budget: string;
  deployment_target: string;
  optimization_priority: string;
}

export interface CostItem {
  item: string;
  monthly_cost_usd: number;
  share_percentage: number;
}

export interface ChecklistItem {
  id: string;
  category: string;
  task: string;
  description: string;
  criticality: string;
  completed: boolean;
}

export interface ReadinessSummary {
  ready: boolean;
  pass_count: number;
  warn_count: number;
  risk_summary: string;
  overall_confidence: number | null;
}

export interface ReportArchitectureSummary {
  components: Record<string, string>;
  estimated_monthly_cost: string;
}

export interface TradeOff {
  benefit: string;
  compromise: string;
}

export interface Alternative {
  architecture_name: string;
  rejection_reason: string;
}

export interface ReportMetrics {
  overall_score: number | null;
  benchmark_score: number | null;
  evaluation_score: number | null;
  success_rate: number | null;
  median_latency_ms: number | null;
  throughput_qps: number | null;
}

export interface ArchitectureReport {
  id: string;
  title: string;
  generated_at: string;
  project_info: ProjectInfo;
  architecture_summary: ReportArchitectureSummary;
  readiness_summary: ReadinessSummary;
  metrics: ReportMetrics;
  trade_offs: TradeOff[];
  alternatives: Alternative[];
  deployment_checklist: ChecklistItem[];
  cost_breakdown: CostItem[] | null;
}
