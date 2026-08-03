"""Completeness metric calculator for Forge evaluation module."""

import logging
import re
from typing import Any, List, Optional, Set

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)

_STOPWORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in",
    "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the",
    "their", "then", "there", "these", "they", "this", "to", "was", "will", "with",
    "what", "where", "when", "why", "how", "who", "which",
}


class CompletenessCalculator(MetricCalculator):
    """Metric evaluating how thoroughly the answer covers the information required by the question."""

    @property
    def metric_name(self) -> str:
        return "completeness"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        return "Measures how completely the generated answer covers all aspects of the question."

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            is_valid, err = self.validate_inputs(metric_input, required_fields=["question", "answer"])
            if not is_valid:
                return self.build_result(score=0.0, success=False, error_message=err)

            target_provider = (metric_input.metadata.get("provider") or "").lower()

            with self.measure_execution_time() as timer:
                if target_provider in ("deterministic", "deterministic_fallback", "fallback"):
                    return self._deterministic(metric_input, timer)

                score = self._try_ragas(metric_input)
                if score is not None:
                    return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"provider_used": "ragas"})
                return self._deterministic(metric_input, timer)

        except Exception as exc:
            logger.error("CompletenessCalculator unhandled error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))

    def _try_ragas(self, metric_input: MetricInput) -> Optional[float]:
        try:
            from app.metrics.ragas_metrics import RagasEvaluator
            from app.schemas.evaluation import EvaluationRequest
            evaluator = RagasEvaluator()
            req = EvaluationRequest(question=metric_input.question or "", answer=metric_input.answer or "",
                                    contexts=metric_input.contexts, ground_truth=metric_input.ground_truth)
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "answer_relevancy" in scores:
                return float(scores["answer_relevancy"])
        except Exception as exc:
            logger.warning("RAGAS completeness failed: %s", exc)
        return None

    def _deterministic(self, metric_input: MetricInput, timer: Any) -> MetricResult:
        q_words = set(self._extract_keywords(metric_input.question or ""))
        a_words = set(self._extract_keywords(metric_input.answer or ""))

        if not q_words:
            return self.build_result(score=1.0, latency_ms=timer.elapsed_ms, success=True,
                                     metadata={"provider_used": "deterministic_fallback",
                                               "coverage": 1.0, "missing": []})

        # If ground truth provided, measure coverage against ground truth instead
        ref_words = set(self._extract_keywords(metric_input.ground_truth or "")) if metric_input.ground_truth else q_words
        covered = [w for w in ref_words if w in a_words]
        missing = [w for w in ref_words if w not in a_words]
        coverage = len(covered) / len(ref_words) if ref_words else 1.0

        # Length-based completeness boost
        ans_len = len((metric_input.answer or "").split())
        length_factor = min(1.0, ans_len / max(1, len((metric_input.question or "").split()) * 2))
        composite = (coverage * 0.8) + (length_factor * 0.2)

        score = self.normalize_score(composite)
        return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                 metadata={"provider_used": "deterministic_fallback",
                                           "coverage": round(coverage, 4), "missing": missing})
