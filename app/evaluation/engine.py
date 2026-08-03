"""EvaluationEngine: production-grade RAG evaluation orchestrator for Forge."""

from datetime import datetime, timezone
import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from app.evaluation.metrics.base_metric import MetricInput, MetricResult
from app.evaluation.provider_cache import ProviderResultCache
from app.evaluation.registry import MetricCalculatorRegistry, build_default_registry
from app.metrics.ragas_metrics import get_ragas_evaluator
from app.metrics import PassFailStatus
from app.schemas.evaluation import (
    ComprehensiveEvaluationReport,
    EvaluationRequest,
    EvaluationSummarySchema,
    GenerationMetricsSchema,
    OperationalMetricsSchema,
    RetrievalMetricsSchema,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Default weights (must sum to ≤ 1.0; operational metrics excluded from quality score)
# ─────────────────────────────────────────────
_DEFAULT_QUALITY_WEIGHTS: Dict[str, float] = {
    "faithfulness": 0.20,
    "answer_relevancy": 0.20,
    "context_precision": 0.15,
    "context_recall": 0.15,
    "groundedness": 0.10,
    "hallucination_score": 0.05,
    "completeness": 0.05,
    "coherence": 0.05,
    "precision_at_k": 0.02,
    "recall_at_k": 0.01,
    "mrr": 0.01,
    "ndcg": 0.01,
    "hit_rate": 0.00,
}

# Operational metric names excluded from quality scoring
_OPERATIONAL_METRIC_NAMES = frozenset({
    "latency_ms", "token_usage", "estimated_cost_usd", "throughput_tokens_per_second"
})


def _assign_quality_grade(score: float) -> str:
    """Return letter grade based on overall quality score."""
    if score >= 0.97:
        return "A+"
    elif score >= 0.90:
        return "A"
    elif score >= 0.80:
        return "B"
    elif score >= 0.70:
        return "C"
    elif score >= 0.55:
        return "D"
    return "F"


def _assign_deployment_readiness(score: float) -> str:
    """Return deployment readiness tier based on overall quality score."""
    if score >= 0.90:
        return "Production Ready"
    elif score >= 0.80:
        return "Pilot Ready"
    elif score >= 0.65:
        return "Prototype"
    elif score >= 0.50:
        return "Experimental"
    return "Research Only"


def _generate_strengths(scores: Dict[str, float]) -> List[str]:
    strengths: List[str] = []
    if scores.get("faithfulness", 0.0) >= 0.90:
        strengths.append("Excellent factual grounding with high context adherence.")
    if scores.get("groundedness", 0.0) >= 0.90:
        strengths.append("Every claim in the answer is attributable to a retrieved source.")
    if scores.get("hallucination_score", 0.0) >= 0.90:
        strengths.append("Near-zero hallucination detected in generated answers.")
    if scores.get("answer_relevancy", 0.0) >= 0.85:
        strengths.append("Highly relevant generated responses directly answering the prompt.")
    if scores.get("context_precision", 0.0) >= 0.85:
        strengths.append("Highly precise retrieved context with minimal noise.")
    if scores.get("context_recall", 0.0) >= 0.85:
        strengths.append("Comprehensive context retrieval covering all required concepts.")
    if scores.get("coherence", 0.0) >= 0.80:
        strengths.append("Well-structured and coherent generated responses.")
    if scores.get("completeness", 0.0) >= 0.85:
        strengths.append("Answers comprehensively cover all aspects of the question.")
    if scores.get("mrr", 0.0) >= 0.85:
        strengths.append("Excellent retrieval ranking — most relevant document appears near the top.")
    return strengths


def _generate_weaknesses(scores: Dict[str, float]) -> List[str]:
    weaknesses: List[str] = []
    if scores.get("faithfulness", 1.0) < 0.70:
        weaknesses.append("Generated answer contains claims not fully supported by retrieved context.")
    if scores.get("groundedness", 1.0) < 0.70:
        weaknesses.append("Multiple answer claims lack clear attribution to retrieved sources.")
    if scores.get("hallucination_score", 1.0) < 0.70:
        weaknesses.append("Significant hallucination detected — answer includes ungrounded content.")
    if scores.get("answer_relevancy", 1.0) < 0.70:
        weaknesses.append("Generated answer only partially addresses the user question.")
    if scores.get("context_precision", 1.0) < 0.60:
        weaknesses.append("Retrieved contexts include significant noisy or irrelevant chunks.")
    if scores.get("context_recall", 1.0) < 0.60:
        weaknesses.append("Retriever missed important supporting information.")
    if scores.get("coherence", 1.0) < 0.60:
        weaknesses.append("Generated answers lack logical structure or fluency.")
    if scores.get("completeness", 1.0) < 0.60:
        weaknesses.append("Answers do not fully cover all aspects of the question.")
    if scores.get("precision_at_k", 1.0) < 0.50:
        weaknesses.append("Retriever returns many irrelevant documents (low Precision@K).")
    if scores.get("recall_at_k", 1.0) < 0.50:
        weaknesses.append("Retriever misses many relevant documents (low Recall@K).")
    if scores.get("mrr", 1.0) < 0.50:
        weaknesses.append("First relevant document appears too far down the ranked list.")
    if scores.get("ndcg", 1.0) < 0.50:
        weaknesses.append("Overall retrieval ranking quality is below acceptable threshold.")
    return weaknesses


def _generate_recommendations(scores: Dict[str, float]) -> List[str]:
    recs: List[str] = []
    if scores.get("context_recall", 1.0) < 0.60:
        recs.append("Increase retrieval depth (top_k) or optimize query expansion to capture missing information.")
    if scores.get("context_precision", 1.0) < 0.60:
        recs.append("Introduce a reranker or tighten similarity thresholds to filter noisy chunks.")
    if scores.get("faithfulness", 1.0) < 0.70:
        recs.append("Enforce stricter system prompt grounding and context-only generation constraints.")
    if scores.get("groundedness", 1.0) < 0.70:
        recs.append("Add citation-grounding instructions to the generation prompt.")
    if scores.get("hallucination_score", 1.0) < 0.70:
        recs.append("Improve retrieved context quality or add hallucination detection post-processing.")
    if scores.get("answer_relevancy", 1.0) < 0.70:
        recs.append("Refine prompt templates to focus generation on addressing the user query.")
    if scores.get("coherence", 1.0) < 0.60:
        recs.append("Improve LLM selection or prompt engineering for structured response generation.")
    if scores.get("completeness", 1.0) < 0.60:
        recs.append("Instruct the LLM to comprehensively address all aspects of the question.")
    if scores.get("precision_at_k", 1.0) < 0.50:
        recs.append("Improve the retriever model or add a reranking stage.")
    if scores.get("recall_at_k", 1.0) < 0.50:
        recs.append("Increase retrieval depth or use hybrid retrieval (dense + sparse).")
    if scores.get("mrr", 1.0) < 0.50 or scores.get("ndcg", 1.0) < 0.50:
        recs.append("Improve retrieval ranking: consider a cross-encoder reranker.")
    return recs


class EvaluationEngine:
    """Core evaluation orchestrator for Forge RAG Evaluation Module v2.0."""

    def __init__(
        self,
        registry: Optional[MetricCalculatorRegistry] = None,
        default_weights: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initialize EvaluationEngine with registry auto-discovery."""
        self._registry = registry or build_default_registry()
        self._default_weights = default_weights or _DEFAULT_QUALITY_WEIGHTS
        logger.info(
            "EvaluationEngine initialized with %d metric calculators: %s",
            len(self._registry),
            self._registry.metric_names,
        )

    # kept for backward-compat with Phase 3 tests
    @property
    def _calculators(self) -> List:
        return self._registry.all()

    def _extract_weights(self, request: EvaluationRequest) -> Dict[str, float]:
        weights = dict(self._default_weights)
        if request.metric_config:
            for cfg in request.metric_config:
                key = cfg.metric_type.value if hasattr(cfg.metric_type, "value") else str(cfg.metric_type)
                if key in weights:
                    weights[key] = float(cfg.weight)
        total = sum(v for k, v in weights.items() if k not in _OPERATIONAL_METRIC_NAMES)
        if total > 0:
            return {k: (v / total if k not in _OPERATIONAL_METRIC_NAMES else 0.0)
                    for k, v in weights.items()}
        return dict(self._default_weights)

    def _build_metric_input(
        self, request: EvaluationRequest, provider_cache: Optional[ProviderResultCache] = None
    ) -> MetricInput:
        provider_name = request.provider.value if hasattr(request.provider, "value") else str(request.provider)
        return MetricInput(
            question=request.question,
            answer=request.answer,
            contexts=request.contexts,
            ground_truth=request.ground_truth,
            metadata={"provider": provider_name, "provider_cache": provider_cache},
        )

    def _run_all_metrics(self, metric_input: MetricInput) -> Dict[str, MetricResult]:
        results: Dict[str, MetricResult] = {}
        for calc in self._registry.all():
            try:
                results[calc.metric_name] = calc.evaluate(metric_input)
            except Exception as exc:
                logger.error("Fault isolation: calculator '%s' failed: %s", calc.metric_name, exc, exc_info=True)
                results[calc.metric_name] = MetricResult(
                    metric_name=calc.metric_name,
                    category=calc.metric_category,
                    score=0.0,
                    success=False,
                    error_message=str(exc),
                )
        return results

    def _build_execution_metadata(
        self, results: Dict[str, MetricResult]
    ) -> Tuple[List[str], List[str], Dict[str, Any], Dict[str, List[str]], List[str], List[str], float]:
        successful, failed = [], []
        exec_summary: Dict[str, Any] = {}
        provider_map: Dict[str, List[str]] = defaultdict(list)
        providers_used: List[str] = []
        fallback_metrics: List[str] = []
        latencies: List[float] = []

        for name, res in results.items():
            if res.success:
                successful.append(name)
            else:
                failed.append(name)

            provider = res.metadata.get("provider_used", "unknown") if res.metadata else "unknown"
            exec_summary[name] = {
                "success": res.success,
                "score": res.score,
                "latency_ms": res.latency_ms,
                "provider_used": provider,
                "error": res.error_message,
            }
            provider_map[provider].append(name)
            if "deterministic" in provider:
                fallback_metrics.append(name)
            latencies.append(res.latency_ms)

        providers_used = list(provider_map.keys())
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        avg_latency_reported = round(avg_latency, 2)
        if avg_latency_reported == 0.0 and latencies:
            avg_latency_reported = round(avg_latency, 4)
            if avg_latency_reported == 0.0:
                avg_latency_reported = 0.01
        return successful, failed, exec_summary, dict(provider_map), providers_used, fallback_metrics, avg_latency_reported

    def _build_schemas(self, flat: Dict[str, float], ms: float) -> Tuple[RetrievalMetricsSchema, GenerationMetricsSchema, OperationalMetricsSchema]:
        retrieval = RetrievalMetricsSchema(
            precision_at_k=flat.get("precision_at_k", 0.0),
            recall_at_k=flat.get("recall_at_k", 0.0),
            hit_rate=flat.get("hit_rate", 0.0),
            mrr=flat.get("mrr", 0.0),
            ndcg=flat.get("ndcg", 0.0),
        )
        generation = GenerationMetricsSchema(
            faithfulness=flat.get("faithfulness", 0.0),
            answer_relevancy=flat.get("answer_relevancy", 0.0),
            context_precision=flat.get("context_precision", 0.0),
            context_recall=flat.get("context_recall", 0.0),
            groundedness=flat.get("groundedness", 0.0),
            hallucination_score=flat.get("hallucination_score", 0.0),
            completeness=flat.get("completeness", 0.0),
            coherence=flat.get("coherence", 0.0),
        )
        operational = OperationalMetricsSchema(
            total_latency_ms=ms,
            retrieval_latency_ms=flat.get("retrieval_latency_ms", 0.0),
            generation_latency_ms=flat.get("generation_latency_ms", 0.0),
        )
        return retrieval, generation, operational

    def evaluate(self, request: EvaluationRequest) -> ComprehensiveEvaluationReport:
        """Execute all registered metrics with fault isolation and return ComprehensiveEvaluationReport."""
        from uuid import uuid4
        t0 = time.perf_counter()
        evaluation_id = str(uuid4())
        logger.info("Evaluation started for request %s", evaluation_id)

        # Scoped Provider Result Cache for this evaluation request
        provider_cache = ProviderResultCache()

        # Batch RAGAS Execution: Single execution for all RAGAS supported metrics
        ragas_evaluator = get_ragas_evaluator()
        if not ragas_evaluator.is_circuit_open():
            try:
                logger.info("Running batch RAGAS provider evaluation")
                ragas_scores = ragas_evaluator.evaluate(request)
                if isinstance(ragas_scores, dict) and ragas_scores:
                    provider_cache.set_provider_results("ragas", ragas_scores)
                    logger.info(
                        "RAGAS provider cache populated with metrics: %s",
                        list(ragas_scores.keys()),
                    )
            except Exception as exc:
                logger.info("RAGAS batch execution failed / circuit breaker tripped: %s", exc)
        else:
            cooldown_rem = int(ragas_evaluator._circuit_breaker_until - time.time())
            logger.info("RAGAS circuit breaker OPEN (%ds cooldown remaining). Skipping provider call.", max(1, cooldown_rem))

        metric_input = self._build_metric_input(request, provider_cache)
        results = self._run_all_metrics(metric_input)

        # Clear request-scoped cache upon completion
        provider_cache.clear()

        flat_metrics: Dict[str, float] = {k: (r.score if r.success else 0.0) for k, r in results.items()}

        weights = self._extract_weights(request)
        overall_score = sum(
            flat_metrics.get(k, 0.0) * w
            for k, w in weights.items()
            if k not in _OPERATIONAL_METRIC_NAMES
        )
        overall_score = round(max(0.0, min(1.0, overall_score)), 4)

        status = PassFailStatus.PASS if overall_score >= 0.70 else PassFailStatus.FAIL
        quality_grade = _assign_quality_grade(overall_score)
        deployment_readiness = _assign_deployment_readiness(overall_score)

        strengths = _generate_strengths(flat_metrics)
        weaknesses = _generate_weaknesses(flat_metrics)
        recommendations = _generate_recommendations(flat_metrics)

        (successful, failed, exec_summary,
         provider_map, providers_used,
         fallback_metrics, avg_latency) = self._build_execution_metadata(results)

        total_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        retrieval_schema, generation_schema, operational_schema = self._build_schemas(flat_metrics, total_ms)

        summary = EvaluationSummarySchema(
            overall_score=overall_score,
            status=status,
            metric_weights=weights,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
        )

        return ComprehensiveEvaluationReport(
            evaluation_id=evaluation_id,
            evaluation_version="2.0",
            provider=request.provider,
            overall_score=overall_score,
            quality_grade=quality_grade,
            deployment_readiness=deployment_readiness,
            status=status,
            summary=summary,
            retrieval=retrieval_schema,
            generation=generation_schema,
            operational=operational_schema,
            metrics=flat_metrics,
            total_metrics=len(results),
            successful_metrics=successful,
            failed_metrics=failed,
            metric_execution_summary=exec_summary,
            provider_summary=provider_map,
            providers_used=providers_used,
            fallback_metrics=fallback_metrics,
            average_metric_latency_ms=round(avg_latency, 2),
            execution_time_ms=total_ms,
            created_at=datetime.now(timezone.utc),
        )
