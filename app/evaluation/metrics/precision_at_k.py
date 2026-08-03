"""Precision@K retrieval metric calculator for Forge evaluation module."""

import logging
from typing import Any, List, Optional

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class PrecisionAtKCalculator(MetricCalculator):
    """Retrieval metric: Precision@K — proportion of top-K retrieved documents that are relevant."""

    def __init__(self, k: int = 10) -> None:
        self._k = k

    @property
    def metric_name(self) -> str:
        return "precision_at_k"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        return f"Precision@{self._k}: proportion of the top-{self._k} retrieved documents that are relevant."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            is_valid, err = self.validate_inputs(metric_input, required_fields=["retrieved_ids", "relevant_ids"])
            if not is_valid:
                return self.build_result(score=0.0, success=False, error_message=err)

            with self.measure_execution_time() as timer:
                retrieved_k = metric_input.retrieved_ids[:self._k]
                relevant_set = set(metric_input.relevant_ids)
                if not retrieved_k:
                    return self.build_result(score=0.0, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"k": self._k, "retrieved_k": 0, "relevant_in_k": 0})

                hits = [r for r in retrieved_k if r in relevant_set]
                precision = len(hits) / len(retrieved_k)
                score = self.normalize_score(precision)

                return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                         metadata={"k": self._k, "retrieved_k": len(retrieved_k),
                                                   "relevant_in_k": len(hits), "precision": round(precision, 4)})
        except Exception as exc:
            logger.error("PrecisionAtKCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
