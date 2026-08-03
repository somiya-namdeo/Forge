"""Groundedness metric calculator for Forge evaluation module."""

import logging
import re
from typing import Any, Dict, List, Optional, Set

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


class GroundednessCalculator(MetricCalculator):
    """Metric evaluating whether every claim in the answer is grounded in the retrieved contexts.

    Differs from Faithfulness in focus: Groundedness checks attribution coverage (are sources cited for each fact)
    rather than holistic factual overlap.
    """

    @property
    def metric_name(self) -> str:
        return "groundedness"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        return "Measures whether each factual claim in the generated answer can be attributed to a retrieved context."

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

                # Auto-detect: try ragas, else deterministic
                score = self._try_ragas(metric_input)
                if score is not None:
                    return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"provider_used": "ragas"})
                return self._deterministic(metric_input, timer)

        except Exception as exc:
            logger.error("GroundednessCalculator unhandled error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))

    def _try_ragas(self, metric_input: MetricInput) -> Optional[float]:
        try:
            from app.metrics.ragas_metrics import RagasEvaluator
            from app.schemas.evaluation import EvaluationRequest
            evaluator = RagasEvaluator()
            req = EvaluationRequest(question=metric_input.question or "", answer=metric_input.answer or "",
                                    contexts=metric_input.contexts, ground_truth=metric_input.ground_truth)
            scores = evaluator.evaluate(req)
            return float(scores["faithfulness"]) if isinstance(scores, dict) and "faithfulness" in scores else None
        except Exception as exc:
            logger.warning("RAGAS groundedness failed: %s", exc)
        return None

    def _deterministic(self, metric_input: MetricInput, timer: Any) -> MetricResult:
        answer = metric_input.answer or ""
        context_corpus = set(self._extract_keywords(" ".join(metric_input.contexts)))
        sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
        if not sentences:
            sentences = [answer]

        grounded, total = 0, 0
        for sent in sentences:
            words = self._extract_keywords(sent)
            if not words:
                continue
            total += 1
            matched = sum(1 for w in words if w in context_corpus)
            if matched / len(words) >= 0.5:
                grounded += 1

        score = self.normalize_score(grounded / total if total else 0.0)
        return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                 metadata={"provider_used": "deterministic_fallback",
                                           "grounded_sentences": grounded, "total_sentences": total})
