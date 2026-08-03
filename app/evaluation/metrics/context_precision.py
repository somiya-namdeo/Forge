"""Context Precision metric calculator for Forge evaluation module."""

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


class ContextPrecisionCalculator(MetricCalculator):
    """Metric calculator evaluating the proportion of retrieved context chunks that contributed to the response.

    Supports dynamic multi-provider execution:
    1. RAGAS Framework provider (if configured/available).
    2. DeepEval Framework provider (if configured/available).
    3. Deterministic chunk contribution & rank-weighted overlap fallback (LLM-free).
    """

    @property
    def metric_name(self) -> str:
        """Return unique metric name identifier."""
        return "context_precision"

    @property
    def metric_category(self) -> MetricCategory:
        """Return metric category classification."""
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        """Return human-readable metric description."""
        return "Measures the proportion of retrieved contexts that are relevant and contributed to the generated answer."

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract lowercased non-stopword alphanumeric tokens."""
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def _compute_deterministic_fallback(
        self, answer: str, contexts: List[str], question: Optional[str] = None, ground_truth: Optional[str] = None
    ) -> tuple[float, dict[str, Any]]:
        """Compute LLM-free context precision score evaluating per-chunk contribution to answer and ground truth.

        Args:
            answer (str): Generated response answer.
            contexts (List[str]): List of retrieved context chunks.
            question (Optional[str]): User query.
            ground_truth (Optional[str]): Golden reference text.

        Returns:
            tuple[float, dict[str, Any]]: (normalized_score, diagnostic_metadata)
        """
        if not contexts:
            return 0.0, {
                "provider_used": "deterministic_fallback",
                "retrieved_contexts": 0,
                "useful_contexts": 0,
                "ignored_contexts": 0,
                "average_overlap": 0.0,
                "context_scores": [],
            }

        target_text = answer
        if ground_truth:
            target_text += " " + ground_truth
        if question:
            target_text += " " + question

        target_words = set(self._extract_keywords(target_text))
        if not target_words:
            return 0.0, {
                "provider_used": "deterministic_fallback",
                "retrieved_contexts": len(contexts),
                "useful_contexts": 0,
                "ignored_contexts": len(contexts),
                "average_overlap": 0.0,
                "context_scores": [0.0] * len(contexts),
            }

        context_scores: List[float] = []
        useful_count = 0
        ignored_count = 0

        for i, ctx in enumerate(contexts):
            ctx_words = self._extract_keywords(ctx)
            if not ctx_words:
                context_scores.append(0.0)
                ignored_count += 1
                continue

            matched = [w for w in ctx_words if w in target_words]
            overlap = len(matched) / len(ctx_words)

            # Apply rank discount for lower positioned chunks
            rank_discount = 1.0 / (1.0 + 0.1 * i)
            chunk_score = self.normalize_score(overlap * rank_discount)
            context_scores.append(chunk_score)

            if chunk_score >= 0.25:
                useful_count += 1
            else:
                ignored_count += 1

        avg_score = sum(context_scores) / len(context_scores) if context_scores else 0.0
        normalized_total = self.normalize_score(avg_score)

        metadata = {
            "provider_used": "deterministic_fallback",
            "retrieved_contexts": len(contexts),
            "useful_contexts": useful_count,
            "ignored_contexts": ignored_count,
            "average_overlap": round(avg_score, 4),
            "context_scores": context_scores,
        }
        return normalized_total, metadata

    def _try_ragas_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using RAGAS Evaluator provider."""
        try:
            from app.metrics.ragas_metrics import RagasEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = RagasEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "Evaluate context precision",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "context_precision" in scores:
                return float(scores["context_precision"])
        except Exception as exc:
            logger.warning("RAGAS context_precision evaluation failed, falling back to deterministic: %s", exc)
        return None

    def _try_deepeval_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Attempt calculation using DeepEval Evaluator provider."""
        try:
            from app.metrics.deepeval_metrics import DeepEvalEvaluator
            from app.schemas.evaluation import EvaluationRequest

            evaluator = DeepEvalEvaluator()
            req = EvaluationRequest(
                question=metric_input.question or "Evaluate context precision",
                answer=metric_input.answer or "",
                contexts=metric_input.contexts,
                ground_truth=metric_input.ground_truth,
            )
            scores = evaluator.evaluate(req)
            if isinstance(scores, dict) and "context_precision" in scores:
                return float(scores["context_precision"])
        except Exception as exc:
            logger.warning("DeepEval context_precision evaluation failed, falling back to deterministic: %s", exc)
        return None

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        """Execute Context Precision metric calculation.

        Args:
            metric_input (MetricInput): Container containing answer and contexts.

        Returns:
            MetricResult: Calculated score, latency, and metadata.
        """
        try:
            is_valid, err_msg = self.validate_inputs(
                metric_input, required_fields=["answer", "contexts"]
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
                        answer=metric_input.answer or "",
                        contexts=metric_input.contexts,
                        question=metric_input.question,
                        ground_truth=metric_input.ground_truth,
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
                            answer=metric_input.answer or "",
                            contexts=metric_input.contexts,
                            question=metric_input.question,
                            ground_truth=metric_input.ground_truth,
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
            logger.error("Unhandled exception during ContextPrecision calculation: %s", exc, exc_info=True)
            return self.build_result(
                score=0.0,
                success=False,
                error_message=f"Unhandled error in ContextPrecisionCalculator: {exc}",
            )
