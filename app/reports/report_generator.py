import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from app.schemas.report import (
    ArchitectureReport,
    ProjectInfo,
    ArchitectureSummary,
    ReadinessSummary,
    ReportMetrics,
    ChecklistItem,
    CostItem,
    TradeOff,
    Alternative
)


class ReportGenerator:
    """Engine responsible for building comprehensive architecture reports."""

    def generate_report(self, request_data: Dict[str, Any]) -> ArchitectureReport:
        """
        Generate structured ArchitectureReport from Forge session data.
        
        Args:
            request_data: Contains decision_result, benchmark_result, evaluation_result.
        """
        decision = request_data.get("decision_result") or {}
        benchmark = request_data.get("benchmark_result") or {}
        evaluation = request_data.get("evaluation_result") or {}

        # 1. Project Info
        metadata = decision.get("metadata", {})
        project_info = ProjectInfo(
            project_name=metadata.get("project_name", "Forge Project"),
            domain=metadata.get("domain", "general"),
            scale=metadata.get("scale", "prototype"),
            budget=f"${metadata.get('budget_usd', 0)}/mo",
            deployment_target=metadata.get("deployment_target", "aws"),
            optimization_priority=metadata.get("priority", "balanced")
        )

        # 2. Architecture Summary
        components = decision.get("components", {})
        arch_summary = ArchitectureSummary(
            components=components,
            estimated_monthly_cost=decision.get("cost_estimate", "Not Evaluated")
        )

        # 3. Readiness Summary
        conf = decision.get("overall_confidence")
        is_ready = bool(conf and conf > 0.8)
        
        pass_count = 0
        if conf and conf > 0.8: pass_count += 5
        elif conf: pass_count += 3
        
        if benchmark: pass_count += 2
        eval_score = evaluation.get("overall_score")
        if eval_score and eval_score > 0.8: pass_count += 2

        readiness = ReadinessSummary(
            ready=is_ready,
            pass_count=pass_count,
            warn_count=2,
            risk_summary="Ready for Staging" if is_ready else "Review Recommendations",
            overall_confidence=conf
        )

        # 4. Metrics
        stats = benchmark.get("statistics", {})
        metrics = ReportMetrics(
            overall_score=conf,
            benchmark_score=stats.get("average_score"),
            evaluation_score=evaluation.get("overall_score"),
            success_rate=stats.get("success_rate"),
            median_latency_ms=stats.get("average_execution_time_ms"),
            throughput_qps=None # Throughput calculation if present
        )

        # 5. Checklist
        deployment = metadata.get("deployment_target", "aws").lower()
        checklist = [
            ChecklistItem(
                id="chk-1",
                category="Infrastructure",
                task=f"Provision {deployment.upper()} Environment",
                description=f"Set up VPC, subnets, and IAM roles for {deployment.upper()}.",
                criticality="Required",
                completed=False
            ),
            ChecklistItem(
                id="chk-2",
                category="Vector DB",
                task="Deploy Vector Database",
                description=f"Set up and secure the vector database for {components.get('vector_db', 'Vector DB')}.",
                criticality="Required",
                completed=False
            ),
            ChecklistItem(
                id="chk-3",
                category="Security",
                task="Configure API Keys",
                description="Store LLM and external service API keys in a secret manager.",
                criticality="Required",
                completed=False
            )
        ]

        # 6. TradeOffs & Alternatives
        trade_offs = [
            TradeOff(benefit=t.get("benefit", ""), compromise=t.get("compromise", ""))
            for t in decision.get("trade_offs", [])
        ]
        alternatives = [
            Alternative(architecture_name=a.get("architecture_name", ""), rejection_reason=a.get("rejection_reason", ""))
            for a in decision.get("alternatives", [])
        ]

        # 7. Cost Breakdown (Simple estimation logic)
        cost_breakdown = None
        budget = metadata.get("budget_usd")
        if budget:
            cost_breakdown = [
                CostItem(item="Compute", monthly_cost_usd=budget * 0.4, share_percentage=40),
                CostItem(item="Vector DB", monthly_cost_usd=budget * 0.3, share_percentage=30),
                CostItem(item="LLM APIs", monthly_cost_usd=budget * 0.3, share_percentage=30),
            ]

        return ArchitectureReport(
            id=f"report-{uuid.uuid4().hex[:8]}",
            title="Production Readiness Report",
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            project_info=project_info,
            architecture_summary=arch_summary,
            readiness_summary=readiness,
            metrics=metrics,
            trade_offs=trade_offs,
            alternatives=alternatives,
            deployment_checklist=checklist,
            cost_breakdown=cost_breakdown
        )
