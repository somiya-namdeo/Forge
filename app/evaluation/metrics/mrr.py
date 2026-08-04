"""Mean Reciprocal Rank (MRR) metric calculator for Forge evaluation module."""

import logging

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class MRRCalculator(MetricCalculator):
    """Retrieval metric: Mean Reciprocal Rank — measures the rank position of the first relevant result."""

    @property
    def metric_name(self) -> str:
        return "mrr"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        return "Mean Reciprocal Rank: reciprocal of rank position of the first relevant retrieved document."

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
                relevant_set = set(metric_input.relevant_ids)
                if not relevant_set:
                    return self.build_result(score=1.0, latency_ms=timer.elapsed_ms, success=True,
                                             metadata={"first_relevant_rank": None, "mrr": 1.0})

                mrr = 0.0
                first_rank = None
                for i, doc_id in enumerate(metric_input.retrieved_ids, start=1):
                    if doc_id in relevant_set:
                        mrr = 1.0 / i
                        first_rank = i
                        break

                score = self.normalize_score(mrr)
                return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                         metadata={"first_relevant_rank": first_rank,
                                                   "mrr": round(mrr, 4),
                                                   "total_retrieved": len(metric_input.retrieved_ids)})
        except Exception as exc:
            logger.error("MRRCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
