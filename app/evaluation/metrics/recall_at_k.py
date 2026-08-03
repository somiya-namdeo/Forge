"""Recall@K retrieval metric calculator for Forge evaluation module."""

import logging

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class RecallAtKCalculator(MetricCalculator):
    """Retrieval metric: Recall@K — proportion of relevant documents found in top-K retrieved results."""

    def __init__(self, k: int = 10) -> None:
        self._k = k

    @property
    def metric_name(self) -> str:
        return "recall_at_k"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        return f"Recall@{self._k}: proportion of relevant documents that appear in the top-{self._k} results."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            is_valid, err = self.validate_inputs(metric_input, required_fields=["retrieved_ids", "relevant_ids"])
            if not is_valid:
                return self.build_result(score=0.0, success=False, error_message=err)

            with self.measure_execution_time() as timer:
                retrieved_k = set(metric_input.retrieved_ids[:self._k])
                relevant_set = set(metric_input.relevant_ids)
                if not relevant_set:
                    return self.build_result(score=1.0, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"k": self._k, "relevant_count": 0})

                hits = relevant_set & retrieved_k
                recall = len(hits) / len(relevant_set)
                score = self.normalize_score(recall)

                return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                         metadata={"k": self._k, "relevant_count": len(relevant_set),
                                                   "hits": len(hits), "recall": round(recall, 4)})
        except Exception as exc:
            logger.error("RecallAtKCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
