import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from app.schemas.report import (
    ArchitectureReport,
    ProjectInfo,
    ArchitectureDetails,
    ArchitectureRationale
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
        b_val = metadata.get("budget_usd", "")
        budget_display = "Not specified" if not b_val else f"${float(b_val):.0f}/mo"
        
        project_info = ProjectInfo(
            project_name=metadata.get("project_name", "Forge Project"),
            domain=metadata.get("domain", "general"),
            scale=metadata.get("document_scale") or metadata.get("project_scale") or metadata.get("scale", "prototype"),
            budget=budget_display,
            deployment_target=metadata.get("deployment_target", "aws"),
            optimization_priority=metadata.get("priority", "balanced")
        )

        # 2. Architecture Details
        recs = decision.get('recommendations', [])
        components = {}
        rationale = []
        for r in recs:
            if isinstance(r, dict):
                components[r.get('category', 'Unknown')] = r.get('recommended', '')
                rationale.append(ArchitectureRationale(
                    category=r.get('category', 'Unknown'),
                    recommended=r.get('recommended', ''),
                    reason=r.get('reason', 'Selected based on priority constraints.')
                ))
        
        decision_signals = {
            'privacy': metadata.get('privacy', 'false'),
            'low_latency': metadata.get('low_latency', 'false'),
            'enterprise_security': metadata.get('enterprise_security', 'false'),
        }

        arch_details = ArchitectureDetails(
            components=components,
            decision_signals=decision_signals,
            rationale=rationale
        )

        return ArchitectureReport(
            id=f"report-{uuid.uuid4().hex[:8]}",
            title="Architecture Decision Report",
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            project_profile=project_info,
            architecture=arch_details
        )

