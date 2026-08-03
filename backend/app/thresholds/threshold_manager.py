from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from app.metrics import MetricType, PassFailStatus


class ThresholdOperator(str, Enum):
    """Operators for evaluating threshold comparisons."""

    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    EQUAL = "=="


@dataclass
class ThresholdRule:
    """Dataclass defining a single metric quality gate threshold rule.

    Attributes:
        metric_type (MetricType): Target metric enum.
        target_score (float): Target threshold boundary score.
        operator (ThresholdOperator): Comparison operator string/enum.
        warning_score (Optional[float]): Soft boundary score for warning status.
    """

    metric_type: MetricType
    target_score: float
    operator: ThresholdOperator = ThresholdOperator.GREATER_THAN_OR_EQUAL
    warning_score: Optional[float] = None


@dataclass
class ThresholdCheckResult:
    """Dataclass encapsulating single metric threshold evaluation output.

    Attributes:
        metric_type (MetricType): Evaluated metric.
        score (float): Raw metric score.
        target_score (float): Expected threshold target score.
        operator (ThresholdOperator): Operator used.
        status (PassFailStatus): PASS, FAIL, or WARNING status.
        message (str): Detailed failure or warning explanation message.
    """

    metric_type: MetricType
    score: float
    target_score: float
    operator: ThresholdOperator
    status: PassFailStatus
    message: str = ""


class ThresholdManager:
    """Manager for maintaining threshold rules and determining evaluation pass/fail status."""

    def __init__(self, rules: Optional[List[ThresholdRule]] = None) -> None:
        """Initialize ThresholdManager with optional initial rules.

        Args:
            rules (Optional[List[ThresholdRule]]): List of quality gate rules.
        """
        self._rules: Dict[MetricType, ThresholdRule] = {}
        if rules:
            for rule in rules:
                self.register_rule(rule)

    def register_rule(self, rule: ThresholdRule) -> None:
        """Register or update a metric threshold rule.

        Args:
            rule (ThresholdRule): Threshold rule specification.
        """
        self._rules[rule.metric_type] = rule

    def remove_rule(self, metric_type: MetricType) -> bool:
        """Remove threshold rule for a given metric.

        Args:
            metric_type (MetricType): Metric type enum.

        Returns:
            bool: True if rule was found and removed, False otherwise.
        """
        if metric_type in self._rules:
            del self._rules[metric_type]
            return True
        return False

    def get_rule(self, metric_type: MetricType) -> Optional[ThresholdRule]:
        """Get registered threshold rule for a given metric.

        Args:
            metric_type (MetricType): Target metric type.

        Returns:
            Optional[ThresholdRule]: Rule if found, else None.
        """
        return self._rules.get(metric_type)

    def check_metric_threshold(
        self,
        metric_type: MetricType,
        score: float,
    ) -> ThresholdCheckResult:
        """Check a single metric score against registered threshold rule.

        Args:
            metric_type (MetricType): Metric type.
            score (float): Raw score.

        Returns:
            ThresholdCheckResult: Detailed pass/fail check result.
        """
        rule = self._rules.get(metric_type)
        if not rule:
            return ThresholdCheckResult(
                metric_type=metric_type,
                score=score,
                target_score=0.0,
                operator=ThresholdOperator.GREATER_THAN_OR_EQUAL,
                status=PassFailStatus.PASS,
                message="No threshold registered for metric.",
            )

        # Placeholder operator check logic
        status = PassFailStatus.PASS if score >= rule.target_score else PassFailStatus.FAIL
        return ThresholdCheckResult(
            metric_type=metric_type,
            score=score,
            target_score=rule.target_score,
            operator=rule.operator,
            status=status,
            message=f"Score {score} evaluated against threshold {rule.target_score}.",
        )

    def check_all_thresholds(
        self,
        scores: Dict[MetricType, float],
    ) -> List[ThresholdCheckResult]:
        """Check a dictionary of metric scores against all registered threshold rules.

        Args:
            scores (Dict[MetricType, float]): Calculated scores dictionary.

        Returns:
            List[ThresholdCheckResult]: Check results for all evaluated metrics.
        """
        return [
            self.check_metric_threshold(metric, score)
            for metric, score in scores.items()
        ]

    def compute_overall_status(
        self,
        check_results: List[ThresholdCheckResult],
    ) -> PassFailStatus:
        """Determine aggregate overall Pass/Fail/Warning status across all metric results.

        Args:
            check_results (List[ThresholdCheckResult]): Results from threshold checks.

        Returns:
            PassFailStatus: FAIL if any metric failed, WARNING if warning present, else PASS.
        """
        if any(res.status == PassFailStatus.FAIL for res in check_results):
            return PassFailStatus.FAIL
        if any(res.status == PassFailStatus.WARNING for res in check_results):
            return PassFailStatus.WARNING
        return PassFailStatus.PASS
