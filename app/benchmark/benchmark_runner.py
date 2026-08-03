"""Benchmark runner module orchestrating dataset evaluations."""

from pathlib import Path
import random

from app.benchmark.benchmark_models import (
    BenchmarkRunConfig,
    BenchmarkSample,
    BenchmarkSampleResult,
)
from app.datasets.benchmark_loader import BenchmarkLoader
from app.schemas.evaluation import EvaluationRequest
from app.services.evaluation_service import EvaluationService


class BenchmarkRunner:
    """Orchestrator responsible for running evaluation datasets through EvaluationService."""

    def __init__(
        self,
        evaluation_service: EvaluationService,
        loader: BenchmarkLoader,
    ) -> None:
        """Initialize benchmark runner with injected dependencies."""
        self.evaluation_service = evaluation_service
        self.loader = loader

    def _load_samples(self, dataset_path: str | Path | None) -> list[BenchmarkSample]:
        """Load benchmark samples from specified path or default dataset."""
        if dataset_path is None:
            return self.loader.load_default()
        return self.loader.load(dataset_path)

    @staticmethod
    def _build_request(
        sample: BenchmarkSample,
        config: BenchmarkRunConfig,
    ) -> EvaluationRequest:
        """Construct EvaluationRequest payload from BenchmarkSample and config."""
        answer_text = (
            sample.expected_answer
            if sample.expected_answer and sample.expected_answer.strip()
            else sample.ground_truth
        )
        return EvaluationRequest(
            question=sample.question,
            answer=answer_text,
            contexts=sample.contexts,
            ground_truth=sample.ground_truth,
            provider=config.provider,
            metric_config=config.metric_config,
            threshold_config=config.threshold_config,
        )

    def run(
        self,
        benchmark_name: str,
        config: BenchmarkRunConfig,
        dataset_path: str | Path | None = None,
    ) -> list[BenchmarkSampleResult]:
        """Execute benchmark samples and collect evaluation results."""
        _ = benchmark_name  # Preserved for downstream report generation

        samples = self._load_samples(dataset_path)

        if config.shuffle:
            rng = random.Random(42)
            rng.shuffle(samples)

        if config.max_samples is not None:
            samples = samples[: config.max_samples]

        results: list[BenchmarkSampleResult] = []
        for sample in samples:
            request = self._build_request(sample, config)

            try:
                response = self.evaluation_service.evaluate(request)
            except ValueError as exc:
                raise ValueError(
                    f"Benchmark sample evaluation failed for '{sample.sample_id}': {exc}"
                ) from exc

            result = BenchmarkSampleResult(
                sample_id=sample.sample_id,
                evaluation_response=response,
                execution_time_ms=response.execution_time_ms,
            )
            results.append(result)

        return results
