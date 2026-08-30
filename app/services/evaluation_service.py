"""
Evaluation Orchestration Service Module.

Provides reusable single-response evaluation engine routing requests to metric providers
(RAGAS, TruLens, Custom), running threshold quality gates, and computing weighted scores.
"""

from typing import Any, List, Optional
from uuid import uuid4

from app.history.evaluation_history import (
    EvaluationHistoryManager,
    EvaluationRecord,
)
from app.metrics import (
    EvaluationProvider,
    MetricRegistry,
)
from app.metrics.ragas_metrics import RagasEvaluator
from app.schemas.evaluation import (
    EvaluationHistoryFilter,
    EvaluationRequest,
    EvaluationResponse,
    ThresholdConfigSchema,
)
from app.thresholds.threshold_manager import (ThresholdManager,ThresholdRule,)
from app.utils.score_calculator import ScoreCalculator
from app.utils.weighting import WeightConfig, WeightingEngine


class EvaluationService:
    """Reusable engine for evaluating a single RAG response.

    Maintains zero benchmark orchestration logic, delegating dataset loops and batch job management
    to BenchmarkService.
    """

    def __init__(
        self,
        metric_registry: Optional[MetricRegistry] = None,
        threshold_manager: Optional[ThresholdManager] = None,
        score_calculator: Optional[ScoreCalculator] = None,
        history_manager: Optional[EvaluationHistoryManager] = None,
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

    def _register_default_providers(self) -> None:
        """Register built-in evaluation metric providers (RAGAS, TruLens, Custom)."""
        if not self.metric_registry.exists("ragas"):
            self.metric_registry.register_provider(RagasEvaluator())

    def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """Evaluate a single RAG sample response synchronously across configured metrics.

        Args:
            request (EvaluationRequest): Single prompt, answer, contexts, and reference ground truth.

        Returns:
            EvaluationResponse: Calculated metric scores, overall composite score, status, and latency.
        """
        # Delegate single sample evaluation to EvaluationEngine
        if not hasattr(self, "_engine") or self._engine is None:
            from app.evaluation.engine import EvaluationEngine
            self._engine = EvaluationEngine()

        report = self._engine.evaluate(request)

        # Save single evaluation record to history manager
        record = EvaluationRecord(
            evaluation_id=report.evaluation_id,
            rag_architecture_id="single_evaluation",
            dataset_id="single_sample",
            composite_score=report.overall_score,
            overall_status=report.status,
            metrics_summary=report.metrics,
        )
        self.history_manager.save(record)

        return report

    run_evaluation = evaluate

    async def evaluate_async(self, request: EvaluationRequest) -> str:
        """Enqueue asynchronous single evaluation for background worker.

        Args:
            request (EvaluationRequest): Evaluation input payload.

        Returns:
            str: Unique evaluation UUID.
        """
        return str(uuid4())

    run_evaluation_async = evaluate_async

    def get_evaluation_result(self, evaluation_id: str) -> Optional[EvaluationResponse]:
        """Fetch evaluation result by UUID."""
        record = self.history_manager.get_by_id(evaluation_id)
        if not record:
            return None

        return EvaluationResponse(
            evaluation_id=record.evaluation_id,
            provider=EvaluationProvider.RAGAS,
            overall_score=record.composite_score,
            status=record.overall_status,
            metrics=record.metrics_summary,
        )

    def list_evaluation_history(
        self,
        filter_params: EvaluationHistoryFilter,
    ) -> List[EvaluationRecord]:
        """Query evaluation history records."""
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
        """Register quality gate threshold rules."""
        for config in threshold_configs:
            rule = ThresholdRule(
                metric_type=config.metric_type,
                target_score=config.target_score,
                operator=config.operator,
                warning_score=config.warning_score,
            )
            self.threshold_manager.register_rule(rule)

