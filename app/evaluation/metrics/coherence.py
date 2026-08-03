"""Coherence metric calculator for Forge evaluation module."""

import logging
import re
from typing import Any, Optional

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class CoherenceCalculator(MetricCalculator):
    """Metric evaluating the logical structure, flow, and readability of the generated answer."""

    @property
    def metric_name(self) -> str:
        return "coherence"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        return "Measures the logical structure, coherence, and fluency of the generated answer."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            is_valid, err = self.validate_inputs(metric_input, required_fields=["answer"])
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
            logger.error("CoherenceCalculator unhandled error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))

    def _try_deepeval(self, metric_input: MetricInput) -> Optional[float]:
        try:
            from app.metrics.deepeval_metrics import get_deepeval_evaluator
            from app.schemas.evaluation import EvaluationRequest
            evaluator = get_deepeval_evaluator()
            req = EvaluationRequest(question=metric_input.question or "", answer=metric_input.answer or "",
                                    contexts=metric_input.contexts, ground_truth=metric_input.ground_truth)
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "coherence" in scores:
                return float(scores["coherence"])
        except Exception as exc:
            logger.info("DeepEval unavailable/timeout. Using deterministic coherence: %s", exc)
        return None

    def _deterministic(self, metric_input: MetricInput, timer: Any) -> MetricResult:
        answer = metric_input.answer or ""
        sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
        if not sentences:
            return self.build_result(score=0.3, latency_ms=timer.elapsed_ms, success=True,
                                     metadata={"provider_used": "deterministic_fallback",
                                               "sentence_count": 0, "avg_sentence_length": 0})

        # Heuristic 1: sentence count (more sentences → better structure, up to threshold)
        sent_count_score = min(1.0, len(sentences) / 5.0)

        # Heuristic 2: avg sentence length (15–25 words per sentence is optimal)
        word_counts = [len(s.split()) for s in sentences]
        avg_len = sum(word_counts) / len(word_counts)
        if 10 <= avg_len <= 30:
            length_score = 1.0
        elif avg_len < 5:
            length_score = 0.4
        else:
            length_score = 0.7

        # Heuristic 3: transition words present
        transitions = {"however", "therefore", "furthermore", "additionally", "first", "second", "finally",
                       "also", "moreover", "consequently", "although", "because", "since", "thus"}
        words_lower = set(answer.lower().split())
        transition_score = min(1.0, len(transitions & words_lower) / 2.0)

        composite = (sent_count_score * 0.3) + (length_score * 0.4) + (transition_score * 0.3)
        score = self.normalize_score(composite)

        return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                 metadata={"provider_used": "deterministic_fallback",
                                           "sentence_count": len(sentences),
                                           "avg_sentence_length": round(avg_len, 1),
                                           "transition_words_detected": list(transitions & words_lower)})
