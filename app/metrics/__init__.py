"""
Evaluation Metrics Package.

Defines pluggable evaluator interfaces, provider registries, metric types,
and score value containers supporting RAGAS, DeepEval, TruLens, and Custom evaluators.
"""

from enum import Enum
from app.metrics.base import BaseMetricEvaluator
from app.metrics.registry import MetricRegistry


class EvaluationProvider(str, Enum):
    """Supported evaluation provider frameworks."""

    RAGAS = "ragas"
    DEEPEVAL = "deepeval"
    TRULENS = "trulens"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Core RAG evaluation metrics supported across providers."""

    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_RECALL = "context_recall"
    CONTEXT_PRECISION = "context_precision"
    HALLUCINATION = "hallucination"
    TOXICITY = "toxicity"
    LATENCY = "latency"
    COST = "cost"
    CUSTOM = "custom"


class PassFailStatus(str, Enum):
    """Quality gate threshold evaluation status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


__all__ = [
    "EvaluationProvider",
    "MetricType",
    "PassFailStatus",
    "BaseMetricEvaluator",
    "MetricRegistry",
]
