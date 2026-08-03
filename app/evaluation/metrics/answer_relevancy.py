"""Answer Relevancy metric calculator for Forge evaluation module."""

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
    "what", "where", "when", "why", "how", "who", "which", "can", "does", "do",
}


class AnswerRelevancyCalculator(MetricCalculator):
    """Metric calculator evaluating how directly and completely a generated answer addresses the user question.

    Supports dynamic multi-provider execution:
    1. RAGAS Framework provider (if configured/available).
    2. DeepEval Framework provider (if configured/available).
    3. Deterministic keyword-coverage & completeness fallback (LLM-free).
    """

    @property
    def metric_name(self) -> str:
        """Return unique metric name identifier."""
        return "answer_relevancy"

    @property
    def metric_category(self) -> MetricCategory:
        """Return metric category classification."""
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        """Return human-readable metric description."""
        return "Measures how directly and completely the generated answer addresses the user question."

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract lowercased non-stopword alphanumeric tokens."""
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def _compute_deterministic_fallback(
        self, question: str, answer: str
    ) -> tuple[float, dict[str, Any]]:
        """Compute LLM-free answer relevancy score using lexical overlap, keyword coverage, and completeness heuristics.

        Args:
            question (str): User prompt or question.
            answer (str): Generated response text.

        Returns:
            tuple[float, dict[str, Any]]: (normalized_score, diagnostic_metadata)
        """
        q_words = self._extract_keywords(question)
        a_words = set(self._extract_keywords(answer))

        if not q_words:
            return 1.0, {
                "provider_used": "deterministic_fallback",
                "keyword_coverage": 1.0,
                "matched_terms": [],
                "missing_terms": [],
                "completeness_estimate": 1.0,
            }

        q_unique = list(dict.fromkeys(q_words))
        matched = [w for w in q_unique if w in a_words]
        missing = [w for w in q_unique if w not in a_words]

        coverage_ratio = len(matched) / len(q_unique)

        # Completeness heuristic based on answer length and word count
        ans_word_count = len(answer.split())
        if ans_word_count < 3:
            completeness = 0.3
        elif ans_word_count < 6:
            completeness = 0.7
        else:
            completeness = 1.0

        # Weighted combination: 75% keyword coverage + 25% completeness heuristic
        composite = (coverage_ratio * 0.75) + (completeness * 0.25)
        normalized_score = self.normalize_score(composite)

        metadata = {
            "provider_used": "deterministic_fallback",
            "keyword_coverage": round(coverage_ratio, 4),
            "matched_terms": matched,
            "missing_terms": missing,
            "completeness_estimate": completeness,
        }
        return normalized_score, metadata

    def _try_ragas_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using RAGAS Evaluator provider."""
        try:
            from app.metrics.ragas_metrics import RagasEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = RagasEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "answer_relevancy" in scores:
                return float(scores["answer_relevancy"])
        except Exception as exc:
            logger.warning("RAGAS answer_relevancy evaluation failed, falling back to deterministic: %s", exc)
        return None

    def _try_deepeval_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using DeepEval Evaluator provider."""
        try:
            from app.metrics.deepeval_metrics import DeepEvalEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = DeepEvalEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "answer_relevancy" in scores:
                return float(scores["answer_relevancy"])
        except Exception as exc:
            logger.warning("DeepEval answer_relevancy evaluation failed, falling back to deterministic: %s", exc)
        return None

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        """Execute Answer Relevancy metric calculation.

        Args:
            metric_input (MetricInput): Container containing question and answer.

        Returns:
            MetricResult: Calculated score, latency, and metadata.
        """
        try:
            is_valid, err_msg = self.validate_inputs(
                metric_input, required_fields=["question", "answer"]
            )
            if not is_valid:
                return self.build_result(
                    score=0.0,
                    success=False,
                    error_message=err_msg,
                )

            target_provider = (metric_input.metadata.get("provider") or "").lower()

            with self.measure_execution_time() as timer:
                score: Optional[float] = None
                provider_used = "deterministic_fallback"

                if target_provider in ("deterministic", "deterministic_fallback", "fallback"):
                    score, fallback_meta = self._compute_deterministic_fallback(
                        question=metric_input.question or "",
                        answer=metric_input.answer or "",
                    )
                    return self.build_result(
                        score=score,
                        latency_ms=timer.elapsed_ms,
                        success=True,
                        metadata=fallback_meta,
                    )
                elif target_provider == "ragas":
                    score = self._try_ragas_evaluation(metric_input)
                    if score is not None:
                        provider_used = "ragas"
                elif target_provider == "deepeval":
                    score = self._try_deepeval_evaluation(metric_input)
                    if score is not None:
                        provider_used = "deepeval"

                if score is None:
                    # Auto-detect or fallback
                    score = self._try_ragas_evaluation(metric_input)
                    if score is not None:
                        provider_used = "ragas"
                    else:
                        score, fallback_meta = self._compute_deterministic_fallback(
                            question=metric_input.question or "",
                            answer=metric_input.answer or "",
                        )
                        return self.build_result(
                            score=score,
                            latency_ms=timer.elapsed_ms,
                            success=True,
                            metadata=fallback_meta,
                        )

                meta = {
                    "provider_used": provider_used,
                    "target_provider": target_provider or "auto",
                }
                return self.build_result(
                    score=score,
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    metadata=meta,
                )

        except Exception as exc:
            logger.error("Unhandled exception during AnswerRelevancy calculation: %s", exc, exc_info=True)
            return self.build_result(
                score=0.0,
                success=False,
                error_message=f"Unhandled error in AnswerRelevancyCalculator: {exc}",
            )
