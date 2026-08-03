"""
JSON Export Module.

Serializes EvaluationReport instances into standardized JSON format string representations.
"""

import json
from typing import Any, Dict

from app.reports.report_generator import EvaluationReport


class JSONExporter:
    """Exporter for serializing EvaluationReport objects into formatted JSON string or dict."""

    def export_to_dict(self, report: EvaluationReport) -> Dict[str, Any]:
        """Convert EvaluationReport into dictionary representation.

        Args:
            report (EvaluationReport): Report instance.

        Returns:
            Dict[str, Any]: Dictionary payload.
        """
        return {
            "report_id": report.report_id,
            "evaluation_id": report.evaluation_id,
            "title": report.title,
            "summary": report.summary,
            "overall_status": report.overall_status,
            "composite_score": report.composite_score,
            "metric_breakdown": report.metric_breakdown,
            "threshold_results": report.threshold_results,
            "recommendations": report.recommendations,
            "generated_at": report.generated_at.isoformat(),
        }

    def export_to_json(self, report: EvaluationReport, indent: int = 2) -> str:
        """Serialize EvaluationReport into formatted JSON string.

        Args:
            report (EvaluationReport): Report instance.
            indent (int): JSON formatting indentation spaces.

        Returns:
            str: JSON string output.
        """
        data = self.export_to_dict(report)
        return json.dumps(data, indent=indent)
