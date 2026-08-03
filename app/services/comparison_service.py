"""
Comparison service for Forge architecture comparison (v2.0).
"""

from typing import Any, Dict
from app.comparison.comparison_engine import ComparisonEngine
from app.comparison.comparison_models import ComparisonRequest, ComparisonResponse
from app.comparison.comparison_report import ComparisonReportBuilder


class ComparisonService:
    """Service layer for architecture comparison."""

    def __init__(
        self,
        comparison_engine: ComparisonEngine | None = None,
        report_builder: ComparisonReportBuilder | None = None,
    ) -> None:
        """Initialize comparison service."""
        self.comparison_engine = comparison_engine or ComparisonEngine()
        self.report_builder = report_builder or ComparisonReportBuilder()

    def compare(
        self,
        request: ComparisonRequest,
    ) -> ComparisonResponse:
        """Compare architectures and return ComparisonResponse."""
        return self.comparison_engine.compare(request)

    def generate_report(
        self,
        request: ComparisonRequest,
    ) -> Dict[str, Any]:
        """Compare architectures and generate structured report payload."""
        comparison = self.compare(request)
        report = self.report_builder.build_report(comparison)
        if hasattr(report, "model_dump"):
            return report.model_dump()
        return dict(report)