"""
Evaluation Metrics Package.

Defines pluggable evaluator interfaces, provider registries, metric types,
and score value containers supporting RAGAS, TruLens, and Custom evaluators.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from app.metrics.base import BaseMetricEvaluator
from app.metrics.registry import MetricRegistry


class EvaluationProvider(str, Enum):
    """Supported evaluation provider frameworks."""

    RAGAS = "ragas"
    TRULENS = "trulens"
    CUSTOM = "custom"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"
    RAGAS_DETERMINISTIC_FALLBACK = "ragas+deterministic_fallback"


class MetricType(str, Enum):
    """Core RAG evaluation metrics supported across providers."""

    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    LATENCY = "latency"
    COST = "cost"
    CUSTOM = "custom"


class PassFailStatus(str, Enum):
    """Quality gate threshold evaluation status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class MetricValue:
    """Dataclass encapsulating single metric evaluation output."""

    metric_type: MetricType
    score: float
    provider: EvaluationProvider
    status: PassFailStatus = PassFailStatus.PASS
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


__all__ = [
    "EvaluationProvider",
    "MetricType",
    "PassFailStatus",
    "MetricValue",
    "BaseMetricEvaluator",
    "MetricRegistry",
]
