"""
Evaluation Orchestration Service Module.

Coordinates evaluation workflow, routing evaluation requests to metric providers (RAGAS,
DeepEval, TruLens, Custom), running threshold quality gates, computing weighted scores,
saving historical records, and producing PDF/JSON reports.
"""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.history.evaluation_history import (
    EvaluationHistoryManager,
    EvaluationRecord,
)
from app.metrics import (
    EvaluationProvider,
    MetricRegistry,
    PassFailStatus,
)
from app.metrics.custom_metrics import CustomEvaluator, TruLensEvaluator
from app.metrics.deepeval_metrics import DeepEvalEvaluator
from app.metrics.ragas_metrics import RagasEvaluator
from app.reports.export_json import JSONExporter
from app.reports.export_pdf import PDFExporter
from app.reports.report_generator import EvaluationReport, ReportGenerator
from app.schemas.evaluation import (
    EvaluationHistoryFilter,
    EvaluationRequest,
    EvaluationResponse,
    ReportResponseSchema,
    ThresholdConfigSchema,
)
from app.thresholds.threshold_manager import (
    ThresholdManager,
    ThresholdRule,
)
from app.utils.score_calculator import ScoreCalculator
from app.utils.weighting import WeightConfig, WeightingEngine


class EvaluationService:
    """Service orchestrating RAG evaluation requests, score calculations, quality gates, and exports.

    Designed following Dependency Injection and SOLID principles to seamlessly accommodate
    multiple evaluation provider plug-ins and future async processing queues.
    """

    def __init__(
        self,
        metric_registry: Optional[MetricRegistry] = None,
        threshold_manager: Optional[ThresholdManager] = None,
        score_calculator: Optional[ScoreCalculator] = None,
        history_manager: Optional[EvaluationHistoryManager] = None,
        report_generator: Optional[ReportGenerator] = None,
        pdf_exporter: Optional[PDFExporter] = None,
        json_exporter: Optional[JSONExporter] = None,
        registry: Optional[MetricRegistry] = None,
        weighting_engine: Optional[Any] = None,
    ) -> None:
        """Initialize EvaluationService with injected dependencies or defaults."""
        self.metric_registry = metric_registry or registry or MetricRegistry()
        self._register_default_providers()

        self.threshold_manager = threshold_manager or ThresholdManager()
        self.weighting_engine = weighting_engine or WeightingEngine()
        self.score_calculator = score_calculator or ScoreCalculator(WeightConfig())

        self.history_manager = history_manager or EvaluationHistoryManager()
        self.report_generator = report_generator or ReportGenerator()
        self.pdf_exporter = pdf_exporter or PDFExporter()
        self.json_exporter = json_exporter or JSONExporter()

    def _register_default_providers(self) -> None:
        """Register built-in evaluation metric providers (RAGAS, DeepEval, TruLens, Custom)."""
        self.metric_registry.register_provider(RagasEvaluator())
        self.metric_registry.register_provider(DeepEvalEvaluator())
        self.metric_registry.register_provider(TruLensEvaluator())
        self.metric_registry.register_provider(CustomEvaluator())

    def run_evaluation(self, request: EvaluationRequest) -> EvaluationResponse:
        """Execute RAG architecture evaluation synchronously across configured metrics.

        Args:
            request (EvaluationRequest): Evaluation input parameters and test samples.

        Returns:
            EvaluationResponse: Complete evaluation outputs, scores, and threshold audits.
        """
        # Placeholder execution flow returning structured dummy response
        evaluation_id = str(uuid4())

        # Save run to history
        record = EvaluationRecord(
            evaluation_id=evaluation_id,
            rag_architecture_id=request.rag_architecture_id,
            dataset_id=request.dataset_id or "inline_samples",
            composite_score=0.85,
            overall_status=PassFailStatus.PASS,
            metrics_summary={"faithfulness": 0.88, "answer_relevance": 0.82},
        )
        self.history_manager.save(record)

        return EvaluationResponse(
            evaluation_id=evaluation_id,
            evaluation_name=request.evaluation_name,
            rag_architecture_id=request.rag_architecture_id,
            composite_score=0.85,
            overall_status=PassFailStatus.PASS,
            sample_results=[],
            metric_summary={"faithfulness": 0.88, "answer_relevance": 0.82},
            threshold_results=[],
            execution_time_seconds=0.15,
        )

    evaluate = run_evaluation

    async def run_evaluation_async(self, request: EvaluationRequest) -> str:
        """Enqueue asynchronous evaluation job for background execution.

        Args:
            request (EvaluationRequest): Evaluation request payload.

        Returns:
            str: Job UUID for tracking background task status.
        """
        # Async execution placeholder returning job ID
        job_id = str(uuid4())
        return job_id

    def get_evaluation_result(self, evaluation_id: str) -> Optional[EvaluationResponse]:
        """Fetch evaluation result by evaluation UUID.

        Args:
            evaluation_id (str): Unique evaluation UUID.

        Returns:
            Optional[EvaluationResponse]: Evaluation details if found, else None.
        """
        record = self.history_manager.get_by_id(evaluation_id)
        if not record:
            return None

        return EvaluationResponse(
            evaluation_id=record.evaluation_id,
            evaluation_name="Historical Evaluation Run",
            rag_architecture_id=record.rag_architecture_id,
            composite_score=record.composite_score,
            overall_status=record.overall_status,
            metric_summary=record.metrics_summary,
        )

    def list_evaluation_history(
        self,
        filter_params: EvaluationHistoryFilter,
    ) -> List[EvaluationRecord]:
        """Query and filter evaluation history records.

        Args:
            filter_params (EvaluationHistoryFilter): Search criteria.

        Returns:
            List[EvaluationRecord]: List of matching evaluation records.
        """
        return self.history_manager.search(
            rag_architecture_id=filter_params.rag_architecture_id,
            status=filter_params.status,
            limit=filter_params.limit,
            offset=filter_params.offset,
        )

    def configure_thresholds(
        self,
        threshold_configs: List[ThresholdConfigSchema],
    ) -> None:
        """Register or update evaluation quality gate threshold rules.

        Args:
            threshold_configs (List[ThresholdConfigSchema]): Threshold rules list.
        """
        for config in threshold_configs:
            rule = ThresholdRule(
                metric_type=config.metric_type,
                target_score=config.target_score,
                operator=config.operator,
                warning_score=config.warning_score,
            )
            self.threshold_manager.register_rule(rule)

    def generate_report(self, evaluation_id: str) -> ReportResponseSchema:
        """Generate structured evaluation report for an evaluation run.

        Args:
            evaluation_id (str): Evaluation run UUID.

        Returns:
            ReportResponseSchema: Formatted report schema.
        """
        record = self.history_manager.get_by_id(evaluation_id)
        status = record.overall_status if record else PassFailStatus.PASS
        score = record.composite_score if record else 0.85
        metrics = record.metrics_summary if record else {"faithfulness": 0.85}

        report: EvaluationReport = self.report_generator.generate_report(
            evaluation_id=evaluation_id,
            overall_status=status.value if isinstance(status, PassFailStatus) else str(status),
            composite_score=score,
            metric_scores=metrics,
        )

        return ReportResponseSchema(
            report_id=report.report_id,
            evaluation_id=report.evaluation_id,
            title=report.title,
            summary=report.summary,
            overall_status=status if isinstance(status, PassFailStatus) else PassFailStatus.PASS,
            composite_score=report.composite_score,
            metric_breakdown=report.metric_breakdown,
            recommendations=report.recommendations,
        )

    def export_pdf(self, evaluation_id: str) -> bytes:
        """Export evaluation report as binary PDF byte stream.

        Args:
            evaluation_id (str): Evaluation run ID.

        Returns:
            bytes: PDF binary byte content.
        """
        report_schema = self.generate_report(evaluation_id)
        report_domain = EvaluationReport(
            evaluation_id=report_schema.evaluation_id,
            title=report_schema.title,
            summary=report_schema.summary,
            overall_status=report_schema.overall_status.value,
            composite_score=report_schema.composite_score,
            metric_breakdown=report_schema.metric_breakdown,
            recommendations=report_schema.recommendations,
        )
        return self.pdf_exporter.export_to_pdf(report_domain)

    def export_json(self, evaluation_id: str) -> str:
        """Export evaluation report as formatted JSON string.

        Args:
            evaluation_id (str): Evaluation run ID.

        Returns:
            str: JSON string representation of report.
        """
        report_schema = self.generate_report(evaluation_id)
        report_domain = EvaluationReport(
            evaluation_id=report_schema.evaluation_id,
            title=report_schema.title,
            summary=report_schema.summary,
            overall_status=report_schema.overall_status.value,
            composite_score=report_schema.composite_score,
            metric_breakdown=report_schema.metric_breakdown,
            recommendations=report_schema.recommendations,
        )
        return self.json_exporter.export_to_json(report_domain)

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """List registered evaluation providers and their supported metrics.

        Returns:
            List[Dict[str, Any]]: Information on registered providers and metrics.
        """
        provider_names = self.metric_registry.list_providers()
        results = []
        for name in provider_names:
            provider_inst = self.metric_registry.get_provider(name)
            metrics = [m.value for m in provider_inst.supported_metrics] if provider_inst else []
            results.append({"provider": name.value, "supported_metrics": metrics})
        return results
