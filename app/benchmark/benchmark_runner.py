"""Benchmark runner module orchestrating dataset evaluations."""

from pathlib import Path
import random
from typing import Optional

from app.benchmark.benchmark_models import (
    BenchmarkRunConfig,
    BenchmarkSample,
    BenchmarkSampleResult,
)
from app.datasets.benchmark_loader import BenchmarkLoader
from app.schemas.evaluation import EvaluationRequest
from app.services.evaluation_service import EvaluationService


class BenchmarkRunner:
    """Orchestrator responsible for running evaluation datasets through EvaluationService.

    Delegates individual sample metric calculations strictly to EvaluationService.evaluate().
    """

    def __init__(
        self,
        evaluation_service: EvaluationService,
        loader: BenchmarkLoader,
    ) -> None:
        """Initialize benchmark runner with injected dependencies."""
        self.evaluation_service = evaluation_service
        self.loader = loader

    def _load_samples(
        self,
        config: BenchmarkRunConfig,
        dataset_path: Optional[str | Path] = None,
    ) -> list[BenchmarkSample]:
        """Load benchmark samples from inline config samples, specified path, or default dataset."""
        if config.samples and len(config.samples) > 0:
            return config.samples
        if dataset_path is not None:
            return self.loader.load(dataset_path)
        return self.loader.load_default()

    @staticmethod
    def _build_request(
        sample: BenchmarkSample,
        config: BenchmarkRunConfig,
    ) -> EvaluationRequest:
        """Construct single-sample EvaluationRequest payload from BenchmarkSample and config."""
        answer_text = (
            sample.expected_answer
            if sample.expected_answer and sample.expected_answer.strip()
            else sample.ground_truth
        )
        if not answer_text or not answer_text.strip():
            answer_text = f"Evaluated RAG answer for prompt: {sample.question}"

        threshold_cfg = config.threshold_config
        if isinstance(threshold_cfg, list):
            threshold_cfg_list = threshold_cfg
        elif threshold_cfg is not None:
            threshold_cfg_list = [threshold_cfg]
        else:
            threshold_cfg_list = None

        return EvaluationRequest(
            question=sample.question,
            answer=answer_text,
            contexts=sample.contexts if sample.contexts else [],
            ground_truth=sample.ground_truth if sample.ground_truth else None,
            provider=config.provider,
            metric_config=config.metric_config,
            threshold_config=threshold_cfg_list,
        )

    def run(
        self,
        benchmark_name: str,
        config: BenchmarkRunConfig,
        dataset_path: Optional[str | Path] = None,
    ) -> list[BenchmarkSampleResult]:
        """Execute benchmark samples by delegating each sample evaluation to EvaluationService."""
        _ = benchmark_name

        samples = self._load_samples(config, dataset_path)

        if config.shuffle:
            rng = random.Random(42)
            rng.shuffle(samples)

        limit = config.limit_samples or config.max_samples
        if limit is not None:
            samples = samples[:limit]

        results: list[BenchmarkSampleResult] = []
        for sample in samples:
            request = self._build_request(sample, config)

            try:
                # Delegate single evaluation to EvaluationService
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
