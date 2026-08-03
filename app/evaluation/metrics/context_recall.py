"""Context Recall metric calculator for Forge evaluation module."""

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


class ContextRecallCalculator(MetricCalculator):
    """Metric calculator evaluating whether retrieved contexts contain all information necessary to answer the question.

    Supports dynamic multi-provider execution:
    1. RAGAS Framework provider (if configured/available).
    2. DeepEval Framework provider (if configured/available).
    3. Deterministic concept coverage fallback (LLM-free).
    """

    @property
    def metric_name(self) -> str:
        """Return unique metric name identifier."""
        return "context_recall"

    @property
    def metric_category(self) -> MetricCategory:
        """Return metric category classification."""
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        """Return human-readable metric description."""
        return "Measures the extent to which retrieved contexts contain the information necessary to answer the question."

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract lowercased non-stopword alphanumeric tokens."""
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def _compute_deterministic_fallback(
        self,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        answer: Optional[str] = None,
        question: Optional[str] = None,
    ) -> tuple[float, dict[str, Any]]:
        """Compute LLM-free context recall score measuring concept coverage of golden reference in retrieved contexts.

        Args:
            contexts (List[str]): List of retrieved context chunks.
            ground_truth (Optional[str]): Golden reference text.
            answer (Optional[str]): Generated response answer.
            question (Optional[str]): User query prompt.

        Returns:
            tuple[float, dict[str, Any]]: (normalized_score, diagnostic_metadata)
        """
        if not contexts:
            return 0.0, {
                "provider_used": "deterministic_fallback",
                "required_concepts": [],
                "covered_concepts": [],
                "missing_concepts": [],
                "coverage_ratio": 0.0,
                "retrieved_context_count": 0,
            }

        ref_text = ground_truth or ""
        if not ref_text.strip():
            ref_text = (answer or "") + " " + (question or "")

        ref_words = self._extract_keywords(ref_text)
        if not ref_words:
            return 1.0, {
                "provider_used": "deterministic_fallback",
                "required_concepts": [],
                "covered_concepts": [],
                "missing_concepts": [],
                "coverage_ratio": 1.0,
                "retrieved_context_count": len(contexts),
            }

        required_concepts = list(dict.fromkeys(ref_words))
        context_corpus = " ".join(contexts).lower()
        context_words = set(self._extract_keywords(context_corpus))

        covered = [w for w in required_concepts if w in context_words]
        missing = [w for w in required_concepts if w not in context_words]

        coverage_ratio = len(covered) / len(required_concepts)
        normalized_score = self.normalize_score(coverage_ratio)

        metadata = {
            "provider_used": "deterministic_fallback",
            "required_concepts": required_concepts,
            "covered_concepts": covered,
            "missing_concepts": missing,
            "coverage_ratio": round(coverage_ratio, 4),
            "retrieved_context_count": len(contexts),
        }
        return normalized_score, metadata

    def _try_ragas_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using RAGAS Evaluator provider."""
        try:
            from app.metrics.ragas_metrics import RagasEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = RagasEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "Evaluate context recall",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "context_recall" in scores:
                return float(scores["context_recall"])
        except Exception as exc:
            logger.warning("RAGAS context_recall evaluation failed, falling back to deterministic: %s", exc)
        return None

    def _try_deepeval_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using DeepEval Evaluator provider."""
        try:
            from app.metrics.deepeval_metrics import DeepEvalEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = DeepEvalEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "Evaluate context recall",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "context_recall" in scores:
                return float(scores["context_recall"])
        except Exception as exc:
            logger.warning("DeepEval context_recall evaluation failed, falling back to deterministic: %s", exc)
        return None

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        """Execute Context Recall metric calculation.

        Args:
            metric_input (MetricInput): Container containing contexts and reference text.

        Returns:
            MetricResult: Calculated score, latency, and metadata.
        """
        try:
            is_valid, err_msg = self.validate_inputs(
                metric_input, required_fields=["contexts"]
            )
            if not is_valid:
                return self.build_result(
                    score=0.0,
                    success=False,
                    error_message=err_msg,
                )

            # Ensure at least ground_truth or answer or question is provided
            if not (metric_input.ground_truth or metric_input.answer or metric_input.question):
                return self.build_result(
                    score=0.0,
                    success=False,
                    error_message="ContextRecall requires ground_truth, answer, or question for reference concept extraction.",
                )

            target_provider = (metric_input.metadata.get("provider") or "").lower()

            with self.measure_execution_time() as timer:
                score: Optional[float] = None
                provider_used = "deterministic_fallback"

                if target_provider in ("deterministic", "deterministic_fallback", "fallback"):
                    score, fallback_meta = self._compute_deterministic_fallback(
                        contexts=metric_input.contexts,
                        ground_truth=metric_input.ground_truth,
                        answer=metric_input.answer,
                        question=metric_input.question,
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
                            contexts=metric_input.contexts,
                            ground_truth=metric_input.ground_truth,
                            answer=metric_input.answer,
                            question=metric_input.question,
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
            logger.error("Unhandled exception during ContextRecall calculation: %s", exc, exc_info=True)
            return self.build_result(
                score=0.0,
                success=False,
                error_message=f"Unhandled error in ContextRecallCalculator: {exc}",
            )
