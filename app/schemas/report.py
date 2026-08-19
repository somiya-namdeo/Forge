from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectInfo(BaseModel):
    project_name: str
    domain: str
    scale: str
    budget: str
    deployment_target: str
    optimization_priority: str


class CostItem(BaseModel):
    item: str
    monthly_cost_usd: float
    share_percentage: float


class ChecklistItem(BaseModel):
    id: str
    category: str
    task: str
    description: str
    criticality: str
    completed: bool = False


class ReadinessSummary(BaseModel):
    ready: bool
    pass_count: int
    warn_count: int
    risk_summary: str
    overall_confidence: Optional[float] = None


class ArchitectureSummary(BaseModel):
    components: Dict[str, str]
    estimated_monthly_cost: str


class TradeOff(BaseModel):
    benefit: str
    compromise: str


class Alternative(BaseModel):
    architecture_name: str
    rejection_reason: str


class ReportMetrics(BaseModel):
    overall_score: Optional[float] = None
    benchmark_score: Optional[float] = None
    evaluation_score: Optional[float] = None
    success_rate: Optional[float] = None
    median_latency_ms: Optional[float] = None
    throughput_qps: Optional[float] = None


class ArchitectureReport(BaseModel):
    id: str
    title: str
    generated_at: str
    project_info: ProjectInfo
    architecture_summary: ArchitectureSummary
    readiness_summary: ReadinessSummary
    metrics: ReportMetrics
    trade_offs: List[TradeOff] = Field(default_factory=list)
    alternatives: List[Alternative] = Field(default_factory=list)
    deployment_checklist: List[ChecklistItem] = Field(default_factory=list)
    cost_breakdown: Optional[List[CostItem]] = None


class ReportGenerationRequest(BaseModel):
    decision_result: Optional[Dict[str, Any]] = None
    benchmark_result: Optional[Dict[str, Any]] = None
    evaluation_result: Optional[Dict[str, Any]] = None
