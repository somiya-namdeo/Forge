"""Metric calculators package for Forge evaluation module."""

from app.evaluation.metrics.answer_relevancy import AnswerRelevancyCalculator
from app.evaluation.metrics.base_metric import (
    MetricCalculator,
    MetricCategory,
    MetricInput,
    MetricResult,
)
from app.evaluation.metrics.coherence import CoherenceCalculator
from app.evaluation.metrics.completeness import CompletenessCalculator
from app.evaluation.metrics.context_precision import ContextPrecisionCalculator
from app.evaluation.metrics.context_recall import ContextRecallCalculator
from app.evaluation.metrics.faithfulness import FaithfulnessCalculator
from app.evaluation.metrics.groundedness import GroundednessCalculator
from app.evaluation.metrics.hallucination import HallucinationCalculator
from app.evaluation.metrics.hit_rate import HitRateCalculator
from app.evaluation.metrics.mrr import MRRCalculator
from app.evaluation.metrics.ndcg import NDCGCalculator
from app.evaluation.metrics.operational import (
    CostEstimationCalculator,
    LatencyCalculator,
    ThroughputCalculator,
    TokenUsageCalculator,
)
from app.evaluation.metrics.precision_at_k import PrecisionAtKCalculator
from app.evaluation.metrics.recall_at_k import RecallAtKCalculator

__all__ = [
    "MetricCalculator",
    "MetricCategory",
    "MetricInput",
    "MetricResult",
    # Generation
    "FaithfulnessCalculator",
    "AnswerRelevancyCalculator",
    "ContextPrecisionCalculator",
    "ContextRecallCalculator",
    "GroundednessCalculator",
    "HallucinationCalculator",
    "CompletenessCalculator",
    "CoherenceCalculator",
    # Retrieval ranking
    "PrecisionAtKCalculator",
    "RecallAtKCalculator",
    "HitRateCalculator",
    "MRRCalculator",
    "NDCGCalculator",
    # Operational
    "LatencyCalculator",
    "TokenUsageCalculator",
    "CostEstimationCalculator",
    "ThroughputCalculator",
]
