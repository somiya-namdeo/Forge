"""Faithfulness metric calculator for Forge evaluation module."""

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


class FaithfulnessCalculator(MetricCalculator):
    """Metric calculator evaluating the factual alignment of generated answers against retrieved context.

    Supports dynamic multi-provider execution:
    1. RAGAS Framework provider (if configured/available).
    2. Deterministic claim-containment fallback (LLM-free).
    """

    @property
    def metric_name(self) -> str:
        """Return unique metric name identifier."""
        return "faithfulness"

    @property
    def metric_category(self) -> MetricCategory:
        """Return metric category classification."""
        return MetricCategory.GENERATION

    @property
    def description(self) -> str:
        """Return human-readable metric description."""
        return "Measures the factual alignment and grounding of the generated answer against retrieved context."

    def _extract_content_words(self, text: str) -> List[str]:
        """Extract lowercased non-stopword tokens from text."""
        words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
        return [w for w in words if w not in _STOPWORDS and len(w) > 1]

    def _compute_deterministic_fallback(
        self, answer: str, contexts: List[str], ground_truth: Optional[str] = None
    ) -> tuple[float, dict[str, Any]]:
        """Compute LLM-free factual grounding score based on sentence-level claim containment in context.

        Args:
            answer (str): Generated response text.
            contexts (List[str]): List of retrieved context chunks.
            ground_truth (Optional[str]): Golden reference text if available.

        Returns:
            tuple[float, dict[str, Any]]: (score, diagnostic_metadata)
        """
        combined_context = " ".join(contexts)
        if ground_truth:
            combined_context += " " + ground_truth

        context_words = set(self._extract_content_words(combined_context))
        if not context_words:
            return 0.0, {"provider_used": "deterministic_fallback", "reason": "Empty context tokens"}

        # Split answer into sentences
        sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
        if not sentences:
            sentences = [answer]

        sentence_scores: List[float] = []
        grounded_count = 0

        for sent in sentences:
            sent_words = self._extract_content_words(sent)
            if not sent_words:
                continue

            matched_words = [w for w in sent_words if w in context_words]
            overlap_ratio = len(matched_words) / len(sent_words)

            if overlap_ratio >= 0.60:
                grounded_count += 1
                sentence_scores.append(1.0)
            else:
                sentence_scores.append(overlap_ratio)

        final_score = (
            sum(sentence_scores) / len(sentence_scores) if sentence_scores else 0.0
        )

        metadata = {
            "provider_used": "deterministic_fallback",
            "total_sentences": len(sentences),
            "grounded_sentences": grounded_count,
            "claim_overlap_ratio": round(final_score, 4),
        }
        return self.normalize_score(final_score), metadata

    def _try_ragas_evaluation(self, metric_input: MetricInput) -> Optional[float]:
        """Fetch Faithfulness metric score from request-scoped provider cache."""
        cache = metric_input.metadata.get("provider_cache") if metric_input.metadata else None
        if cache:
            cached_score = cache.get("ragas", "faithfulness")
            if cached_score is not None:
                logger.info("Faithfulness from cache")
                return cached_score
        return None

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        """Execute Faithfulness metric calculation.

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
                        ground_truth=metric_input.ground_truth,
                    )
                    return self.build_result(
                        score=score,
                        latency_ms=timer.elapsed_ms,
                        success=True,
                        metadata=fallback_meta,
                    )

                score = self._try_ragas_evaluation(metric_input)
                if score is not None:
                    provider_used = "ragas"
                else:
                    score, fallback_meta = self._compute_deterministic_fallback(
                        answer=metric_input.answer or "",
                        contexts=metric_input.contexts,
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
            logger.error("Unhandled exception during Faithfulness calculation: %s", exc, exc_info=True)
            return self.build_result(
                score=0.0,
                success=False,
                error_message=f"Unhandled error in FaithfulnessCalculator: {exc}",
            )
