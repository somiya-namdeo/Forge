"""Hit Rate metric calculator for Forge evaluation module."""

import logging

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class HitRateCalculator(MetricCalculator):
    """Retrieval metric: Hit Rate — binary indicator whether at least one relevant document is retrieved."""

    def __init__(self, k: int = 10) -> None:
        self._k = k

    @property
    def metric_name(self) -> str:
        return "hit_rate"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        return f"Hit Rate@{self._k}: binary score indicating whether at least one relevant doc appears in top-{self._k}."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            if metric_input.retrieved_ids is None or metric_input.relevant_ids is None:
                return self.build_result(
                    score=0.0,
                    success=True,
                    metadata={"status": "skipped", "reason": "retrieval_ranking_ids_unavailable", "provider_used": "skipped"}
                )

            is_valid, err = self.validate_inputs(metric_input, required_fields=["retrieved_ids", "relevant_ids"])
            if not is_valid:
                return self.build_result(score=0.0, success=False, error_message=err)

            with self.measure_execution_time() as timer:
                retrieved_k = set(metric_input.retrieved_ids[:self._k])
                relevant_set = set(metric_input.relevant_ids)
                if not relevant_set:
                    return self.build_result(score=1.0, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"hit": True, "k": self._k})

                hit = bool(retrieved_k & relevant_set)
                score = 1.0 if hit else 0.0
                return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                         metadata={"hit": hit, "k": self._k,
                                                   "retrieved_count": len(metric_input.retrieved_ids),
                                                   "relevant_count": len(relevant_set)})
        except Exception as exc:
            logger.error("HitRateCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
