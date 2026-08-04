"""NDCG (Normalized Discounted Cumulative Gain) metric calculator for Forge evaluation module."""

import logging
import math
from typing import List

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)


class NDCGCalculator(MetricCalculator):
    """Retrieval metric: NDCG@K — measures ranking quality considering graded relevance and position."""

    def __init__(self, k: int = 10) -> None:
        self._k = k

    @property
    def metric_name(self) -> str:
        return "ndcg"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.RETRIEVAL

    @property
    def description(self) -> str:
        return f"NDCG@{self._k}: Normalized Discounted Cumulative Gain measuring retrieval ranking quality."

    def _dcg(self, relevances: List[float]) -> float:
        """Compute Discounted Cumulative Gain for a ranked list of relevance scores."""
        return sum(rel / math.log2(rank + 2) for rank, rel in enumerate(relevances))

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
                                             metadata={"ndcg": 1.0, "k": self._k, "dcg": 0.0, "idcg": 0.0})

                retrieved_k = metric_input.retrieved_ids[:self._k]
                # Binary relevance: 1 if relevant, 0 otherwise
                relevances = [1.0 if doc_id in relevant_set else 0.0 for doc_id in retrieved_k]
                dcg = self._dcg(relevances)

                # Ideal DCG: all relevant docs ranked first
                ideal_count = min(len(relevant_set), self._k)
                ideal_relevances = [1.0] * ideal_count
                idcg = self._dcg(ideal_relevances)

                ndcg = dcg / idcg if idcg > 0 else 0.0
                score = self.normalize_score(ndcg)

                return self.build_result(score=score, latency_ms=timer.elapsed_ms, success=True,
                                         metadata={"k": self._k, "dcg": round(dcg, 4), "idcg": round(idcg, 4),
                                                   "ndcg": round(ndcg, 4)})
        except Exception as exc:
            logger.error("NDCGCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
