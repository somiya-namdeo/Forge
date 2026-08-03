"""Base metric calculator framework for Forge evaluation module."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Tuple


class MetricCategory(str, Enum):
    """Enumeration of metric classification categories."""

    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    OPERATIONAL = "operational"


@dataclass(frozen=True)
class MetricInput:
    """Standardized input parameters container for metric evaluation."""

    question: Optional[str] = None
    answer: Optional[str] = None
    contexts: List[str] = field(default_factory=list)
    ground_truth: Optional[str] = None
    retrieved_ids: List[str] = field(default_factory=list)
    relevant_ids: List[str] = field(default_factory=list)
    retrieval_latency_ms: float = 0.0
    generation_latency_ms: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    estimated_cost_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MetricResult:
    """Standardized result container produced by metric calculators."""

    metric_name: str
    category: MetricCategory
    score: float
    latency_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class _TimingContextManager:
    """Helper context manager to calculate execution duration in milliseconds."""

    def __enter__(self) -> "_TimingContextManager":
        self._start = time.perf_counter()
        self.elapsed_ms: float = 0.0
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000.0


class MetricCalculator(ABC):
    """Abstract base class for all Forge evaluation metric calculators."""

    @property
    @abstractmethod
    def metric_name(self) -> str:
        """Unique identifier for the evaluation metric."""
        pass

    @property
    @abstractmethod
    def metric_category(self) -> MetricCategory:
        """Category classification (retrieval, generation, operational)."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the metric measures."""
        pass

    @abstractmethod
    def evaluate(self, metric_input: MetricInput) -> MetricResult:
        """Execute metric evaluation calculation on the provided input.

        Args:
            metric_input (MetricInput): Input data container containing query, response,
                contexts, references, or operational stats.

        Returns:
            MetricResult: Calculated metric score, execution latency, and metadata.
        """
        pass

    @staticmethod
    def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Bound and normalize a numeric score to the range [0.0, 1.0]."""
        if max_val <= min_val:
            return 0.0
        clamped = max(min_val, min(max_val, score))
        normalized = (clamped - min_val) / (max_val - min_val)
        return round(normalized, 4)

    @staticmethod
    def measure_execution_time() -> _TimingContextManager:
        """Context manager helper to track execution latency in milliseconds."""
        return _TimingContextManager()

    def validate_inputs(
        self,
        metric_input: MetricInput,
        required_fields: List[str],
    ) -> Tuple[bool, Optional[str]]:
        """Helper to validate that required MetricInput attributes are present and non-empty.

        Args:
            metric_input (MetricInput): The input instance to validate.
            required_fields (List[str]): Field names that must not be None or empty.

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not metric_input:
            return False, "MetricInput instance is None."

        missing: List[str] = []
        for f in required_fields:
            val = getattr(metric_input, f, None)
            if val is None:
                missing.append(f)
            elif isinstance(val, (str, list, dict)) and len(val) == 0:
                missing.append(f)

        if missing:
            return False, f"Missing required fields for '{self.metric_name}': {', '.join(missing)}"

        return True, None

    def build_result(
        self,
        score: float,
        latency_ms: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MetricResult:
        """Helper method to construct a standard MetricResult container."""
        return MetricResult(
            metric_name=self.metric_name,
            category=self.metric_category,
            score=self.normalize_score(score),
            latency_ms=round(latency_ms, 2),
            success=success,
            error_message=error_message,
            metadata=metadata or {},
        )
