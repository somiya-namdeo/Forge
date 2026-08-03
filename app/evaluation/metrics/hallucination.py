"""Hallucination metric calculator for Forge evaluation module."""

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
}


class HallucinationCalculator(MetricCalculator):
    """Metric calculator estimating the proportion of hallucinated (ungrounded) content.

    Score is inverse of grounding: 1.0 means zero hallucination, 0.0 means completely hallucinated.
    """

    @property
    def metric_name(self) -> str:
        return "hallucination_score"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        return "Estimates the proportion of hallucinated content (0.0 = fully hallucinated, 1.0 = zero hallucination)."

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            is_valid, err = self.validate_inputs(metric_input, required_fields=["answer", "contexts"])
            if not is_valid:
                return self.build_result(score=0.0, success=False, error_message=err)

            target_provider = (metric_input.metadata.get("provider") or "").lower()

            with self.measure_execution_time() as timer:
                if target_provider in ("deterministic", "deterministic_fallback", "fallback"):
                    return self._deterministic(metric_input, timer)

                score = self._try_deepeval(metric_input)
                if score is not None:
                    return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"provider_used": "deepeval"})
                return self._deterministic(metric_input, timer)

        except Exception as exc:
            logger.error("HallucinationCalculator unhandled error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))

    def _try_deepeval(self, metric_input: MetricInput) -> Optional[float]:
        try:
            from app.metrics.deepeval_metrics import DeepEvalEvaluator
            from app.schemas.evaluation import EvaluationRequest
            evaluator = DeepEvalEvaluator()
            req = EvaluationRequest(question=metric_input.question or "", answer=metric_input.answer or "",
                                    contexts=metric_input.contexts, ground_truth=metric_input.ground_truth)
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "hallucination" in scores:
                # DeepEval hallucination score is lower = better, invert for our scale
                return self.normalize_score(1.0 - float(scores["hallucination"]))
        except Exception as exc:
            logger.info("DeepEval unavailable/timeout. Using deterministic hallucination_score: %s", exc)
        return None

    def _deterministic(self, metric_input: MetricInput, timer: Any) -> MetricResult:
        answer = metric_input.answer or ""
        context_words = set(self._extract_keywords(" ".join(metric_input.contexts)))
        answer_words = self._extract_keywords(answer)
        if not answer_words:
            return self.build_result(score=1.0, latency_ms=timer.elapsed_ms, success=True,
                                     metadata={"provider_used": "deterministic_fallback",
                                               "ungrounded_ratio": 0.0, "grounded_ratio": 1.0})

        grounded = sum(1 for w in answer_words if w in context_words)
        grounded_ratio = grounded / len(answer_words)
        ungrounded_ratio = round(1.0 - grounded_ratio, 4)
        # hallucination_score = 1 means no hallucination (fully grounded)
        score = self.normalize_score(grounded_ratio)
        return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                 metadata={"provider_used": "deterministic_fallback",
                                           "grounded_ratio": round(grounded_ratio, 4),
                                           "ungrounded_ratio": ungrounded_ratio})
