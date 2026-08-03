"""Operational metric calculators for Forge evaluation module (latency, token usage, cost, throughput)."""

import logging

from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)

logger = logging.getLogger(__name__)

# Cost constants (Groq free-tier approximation)
_COST_PER_1K_INPUT_TOKENS: float = 0.0001
_COST_PER_1K_OUTPUT_TOKENS: float = 0.0002
_LATENCY_BUDGET_MS: float = 5000.0      # 5s acceptable ceiling
_THROUGHPUT_CEILING_TPS: float = 200.0  # tokens per second ceiling for normalization


class LatencyCalculator(MetricCalculator):
    """Operational metric: reports total end-to-end latency from MetricInput execution metadata."""

    @property
    def metric_name(self) -> str:
        return "latency_ms"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.OPERATIONAL

    @property
    def description(self) -> str:
        return "Reports the total end-to-end execution latency in milliseconds. Lower is better (inverted for score)."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            with self.measure_execution_time() as timer:
                total_ms = (
                    metric_input.retrieval_latency_ms + metric_input.generation_latency_ms
                ) or 0.0

                # Score is inverse: lower latency → higher score
                latency_score = self.normalize_score(1.0 - (total_ms / _LATENCY_BUDGET_MS))

                return self.build_result(
                    score=latency_score,
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    metadata={
                        "total_latency_ms": total_ms,
                        "retrieval_latency_ms": metric_input.retrieval_latency_ms,
                        "generation_latency_ms": metric_input.generation_latency_ms,
                        "latency_budget_ms": _LATENCY_BUDGET_MS,
                    },
                )
        except Exception as exc:
            logger.error("LatencyCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))


class TokenUsageCalculator(MetricCalculator):
    """Operational metric: reports prompt and completion token counts from MetricInput execution metadata."""

    @property
    def metric_name(self) -> str:
        return "token_usage"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.OPERATIONAL

    @property
    def description(self) -> str:
        return "Reports prompt and completion token counts. Score reflects token efficiency (lower usage = higher score)."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            with self.measure_execution_time() as timer:
                prompt_tokens = metric_input.prompt_tokens or 0
                completion_tokens = metric_input.completion_tokens or 0
                total_tokens = prompt_tokens + completion_tokens

                # Token efficiency: normalized inverse of total (ceiling = 4000 tokens)
                token_score = self.normalize_score(1.0 - (total_tokens / 4000.0))

                return self.build_result(
                    score=token_score,
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    metadata={
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                    },
                )
        except Exception as exc:
            logger.error("TokenUsageCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))


class CostEstimationCalculator(MetricCalculator):
    """Operational metric: estimates USD API cost from token counts in MetricInput execution metadata."""

    @property
    def metric_name(self) -> str:
        return "estimated_cost_usd"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.OPERATIONAL

    @property
    def description(self) -> str:
        return "Estimates USD API cost from prompt and completion token counts."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            with self.measure_execution_time() as timer:
                if metric_input.estimated_cost_usd and metric_input.estimated_cost_usd > 0:
                    cost = metric_input.estimated_cost_usd
                else:
                    cost = (
                        (metric_input.prompt_tokens / 1000.0) * _COST_PER_1K_INPUT_TOKENS
                        + (metric_input.completion_tokens / 1000.0) * _COST_PER_1K_OUTPUT_TOKENS
                    )

                # Score: cost efficiency — lower cost → higher score (ceiling $0.01)
                cost_score = self.normalize_score(1.0 - (cost / 0.01))

                return self.build_result(
                    score=cost_score,
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    metadata={
                        "estimated_cost_usd": round(cost, 6),
                        "cost_per_1k_input": _COST_PER_1K_INPUT_TOKENS,
                        "cost_per_1k_output": _COST_PER_1K_OUTPUT_TOKENS,
                    },
                )
        except Exception as exc:
            logger.error("CostEstimationCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))


class ThroughputCalculator(MetricCalculator):
    """Operational metric: estimates generation throughput in tokens per second."""

    @property
    def metric_name(self) -> str:
        return "throughput_tokens_per_second"

    @property
    def metric_category(self) -> MetricCategory:
        return MetricCategory.OPERATIONAL

    @property
    def description(self) -> str:
        return "Estimates generation throughput in tokens per second."

    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        try:
            with self.measure_execution_time() as timer:
                gen_ms = metric_input.generation_latency_ms or 0.0
                completion_tokens = metric_input.completion_tokens or 0

                if gen_ms > 0 and completion_tokens > 0:
                    tps = completion_tokens / (gen_ms / 1000.0)
                else:
                    tps = 0.0

                tps_score = self.normalize_score(tps / _THROUGHPUT_CEILING_TPS)

                return self.build_result(
                    score=tps_score,
                    latency_ms=timer.elapsed_ms,
                    success=True,
                    metadata={
                        "throughput_tokens_per_second": round(tps, 2),
                        "completion_tokens": completion_tokens,
                        "generation_latency_ms": gen_ms,
                    },
                )
        except Exception as exc:
            logger.error("ThroughputCalculator error: %s", exc, exc_info=True)
            return self.build_result(score=0.0, success=False, error_message=str(exc))
