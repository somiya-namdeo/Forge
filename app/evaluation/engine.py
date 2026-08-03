"""EvaluationEngine module for orchestrating RAG evaluation metrics."""

from datetime import datetime, timezone
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.evaluation.metrics.answer_relevancy import AnswerRelevancyCalculator
from app.evaluation.metrics.base_metric import MetricInput, MetricResult
from app.evaluation.metrics.context_precision import ContextPrecisionCalculator
from app.evaluation.metrics.context_recall import ContextRecallCalculator
from app.evaluation.metrics.faithfulness import FaithfulnessCalculator
from app.metrics import EvaluationProvider, PassFailStatus
from app.schemas.evaluation import (
    ComprehensiveEvaluationReport,
    EvaluationRequest,
    EvaluationResponse,
    EvaluationSummarySchema,
    GenerationMetricsSchema,
    OperationalMetricsSchema,
    RetrievalMetricsSchema,
)

logger = logging.getLogger(__name__)

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "faithfulness": 0.30,
    "answer_relevancy": 0.30,
    "context_precision": 0.20,
    "context_recall": 0.20,
}


class EvaluationEngine:
    """Engine responsible for orchestrating independent metric calculators, fault isolation, and report synthesis."""

    def __init__(self, default_weights: Optional[Dict[str, float]] = None) -> None:
        """Initialize EvaluationEngine with registered metric calculators and configurable weights."""
        self._calculators = [
            FaithfulnessCalculator(),
            AnswerRelevancyCalculator(),
            ContextPrecisionCalculator(),
            ContextRecallCalculator(),
        ]
        self._default_weights = default_weights or _DEFAULT_WEIGHTS

    def _extract_metric_weights(self, request: EvaluationRequest) -> Dict[str, float]:
        """Extract and normalize metric weights from request or configuration."""
        weights = dict(self._default_weights)
        if request.metric_config:
            for cfg in request.metric_config:
                m_type = cfg.metric_type.value if hasattr(cfg.metric_type, "value") else str(cfg.metric_type)
                if m_type in weights:
                    weights[m_type] = float(cfg.weight)

        total = sum(weights.values())
        if total > 0:
            return {k: v / total for k, v in weights.items()}
        return dict(self._default_weights)

    def _generate_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Generate automated strengths based on high-performing metric scores."""
        strengths: List[str] = []
        if scores.get("faithfulness", 0.0) >= 0.90:
            strengths.append("Excellent factual grounding with high context adherence.")
        if scores.get("answer_relevancy", 0.0) >= 0.85:
            strengths.append("Highly relevant generated response directly answering the prompt.")
        if scores.get("context_precision", 0.0) >= 0.85:
            strengths.append("Highly relevant retrieved context chunks with low noise.")
        if scores.get("context_recall", 0.0) >= 0.85:
            strengths.append("Comprehensive context retrieval covering all required golden concepts.")
        return strengths

    def _generate_weaknesses(self, scores: Dict[str, float]) -> List[str]:
        """Generate automated weaknesses based on low-performing metric scores."""
        weaknesses: List[str] = []
        if scores.get("faithfulness", 1.0) < 0.70:
            weaknesses.append("Answer contains claims not fully supported by retrieved context.")
        if scores.get("answer_relevancy", 1.0) < 0.70:
            weaknesses.append("Generated answer only partially addresses the user question.")
        if scores.get("context_precision", 1.0) < 0.60:
            weaknesses.append("Retrieved contexts contain significant noisy or irrelevant chunks.")
        if scores.get("context_recall", 1.0) < 0.60:
            weaknesses.append("Retriever missed important supporting information required for completeness.")
        return weaknesses

    def _generate_recommendations(self, scores: Dict[str, float]) -> List[str]:
        """Generate automated recommendations based on identified metric gaps."""
        recs: List[str] = []
        if scores.get("context_recall", 1.0) < 0.60:
            recs.append("Increase retrieval depth (top_k) or optimize query expansion to capture missing supporting information.")
        if scores.get("context_precision", 1.0) < 0.60:
            recs.append("Introduce a reranker or tighten vector similarity thresholds to filter out noisy chunks.")
        if scores.get("faithfulness", 1.0) < 0.70:
            recs.append("Enforce stricter system prompt grounding and context-only generation constraints.")
        if scores.get("answer_relevancy", 1.0) < 0.70:
            recs.append("Refine prompt templates to focus generation on the user query.")
        return recs

    def evaluate(self, request: EvaluationRequest) -> ComprehensiveEvaluationReport:
        """Execute independent evaluation metrics with fault isolation and assemble ComprehensiveEvaluationReport.

        Args:
            request (EvaluationRequest): Single evaluation request containing question, answer, contexts, and reference.

        Returns:
            ComprehensiveEvaluationReport: Fully populated production report schema.
        """
        t0 = time.perf_counter()
        evaluation_id = str(uuid4())

        provider_name = request.provider.value if hasattr(request.provider, "value") else str(request.provider)
        metric_input = MetricInput(
            question=request.question,
            answer=request.answer,
            contexts=request.contexts,
            ground_truth=request.ground_truth,
            metadata={"provider": provider_name},
        )

        results: Dict[str, MetricResult] = {}

        # Independent execution with fault isolation
        for calc in self._calculators:
            try:
                res = calc.evaluate(metric_input)
                results[calc.metric_name] = res
            except Exception as exc:
                logger.error(
                    "Fault isolation triggered: calculator '%s' failed unexpectedly: %s",
                    calc.metric_name,
                    exc,
                    exc_info=True,
                )
                results[calc.metric_name] = MetricResult(
                    metric_name=calc.metric_name,
                    category=calc.metric_category,
                    score=0.0,
                    success=False,
                    error_message=str(exc),
                )

        # Extract metric scores map
        flat_metrics: Dict[str, float] = {}
        for m_name, res in results.items():
            if res.success:
                flat_metrics[m_name] = res.score
            else:
                flat_metrics[m_name] = 0.0

        # Weighted composite overall_score calculation
        weights = self._extract_metric_weights(request)
        weighted_score = sum(flat_metrics.get(k, 0.0) * w for k, w in weights.items())
        overall_score = round(max(0.0, min(1.0, weighted_score)), 4)

        status = PassFailStatus.PASS if overall_score >= 0.70 else PassFailStatus.FAIL

        # Diagnostic feedback
        strengths = self._generate_strengths(flat_metrics)
        weaknesses = self._generate_weaknesses(flat_metrics)
        recommendations = self._generate_recommendations(flat_metrics)

        total_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # Structured Category Schemas
        retrieval_schema = RetrievalMetricsSchema()

        generation_schema = GenerationMetricsSchema(
            faithfulness=flat_metrics.get("faithfulness", 0.0),
            answer_relevancy=flat_metrics.get("answer_relevancy", 0.0),
            context_precision=flat_metrics.get("context_precision", 0.0),
            context_recall=flat_metrics.get("context_recall", 0.0),
        )

        operational_schema = OperationalMetricsSchema(
            total_latency_ms=total_latency_ms,
        )

        summary_schema = EvaluationSummarySchema(
            overall_score=overall_score,
            status=status,
            metric_weights=weights,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

        report = ComprehensiveEvaluationReport(
            evaluation_id=evaluation_id,
            provider=request.provider,
            overall_score=overall_score,
            status=status,
            summary=summary_schema,
            retrieval=retrieval_schema,
            generation=generation_schema,
            operational=operational_schema,
            metrics=flat_metrics,
            execution_time_ms=total_latency_ms,
            created_at=datetime.now(timezone.utc),
        )

        return report
