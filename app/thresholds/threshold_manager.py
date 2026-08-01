"""Threshold manager for evaluating metric scores against quality gates."""

from app.schemas.evaluation import EvaluationStatus, MetricResult, ThresholdConfig

_WARNING_THRESHOLD_FACTOR = 0.90


class ThresholdManager:
    """Manager responsible for evaluating metric scores against configured thresholds."""

    def evaluate_metric(
        self,
        metric_name: str,
        score: float,
        thresholds: ThresholdConfig,
    ) -> MetricResult:
        """Evaluate a single metric score against configured threshold rules."""
        if metric_name not in ThresholdConfig.model_fields:
            raise ValueError(f"Unsupported metric: '{metric_name}'.")

        target_threshold = float(getattr(thresholds, metric_name))
        warning_boundary = target_threshold * _WARNING_THRESHOLD_FACTOR

        if score >= target_threshold:
            status = EvaluationStatus.PASS
        elif score >= warning_boundary:
            status = EvaluationStatus.WARNING
        else:
            status = EvaluationStatus.FAIL

        description = f"Score {score:.4f} evaluated against threshold {target_threshold:.4f}."

        return MetricResult(
            name=metric_name,
            score=score,
            threshold=target_threshold,
            status=status,
            description=description,
        )

    def overall_status(self, metrics: list[MetricResult]) -> EvaluationStatus:
        """Determine overall aggregate status from evaluated metric results."""
        if any(m.status == EvaluationStatus.FAIL for m in metrics):
            return EvaluationStatus.FAIL
        if any(m.status == EvaluationStatus.WARNING for m in metrics):
            return EvaluationStatus.WARNING
        return EvaluationStatus.PASS
