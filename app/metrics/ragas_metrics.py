"""RAGAS metric evaluator provider implementation."""

from collections.abc import Sequence
import math
from typing import Any

from datasets import Dataset
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from ragas.metrics.base import Metric

from app.core.config import EMBEDDING_MODEL, GROQ_API_KEY, LLM_MODEL
from app.metrics.base import BaseMetricEvaluator
from app.schemas.evaluation import EvaluationRequest

_REFERENCE_REQUIRED_METRICS = {
    "context_precision",
    "context_recall",
}


class RagasEvaluator(BaseMetricEvaluator):
    """RAGAS framework metric evaluation provider using shared Groq LLM configuration."""

    _METRIC_MAP: dict[str, Metric] = {
        "faithfulness": faithfulness,
        "answer_relevancy": answer_relevancy,
        "context_precision": context_precision,
        "context_recall": context_recall,
    }

    def __init__(self) -> None:
        """Initialize RAGAS evaluator and configure Groq LLM and embeddings wrappers."""
        llm = ChatOpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            model=LLM_MODEL,
        )
        embeddings = HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL)
        self._ragas_llm = LangchainLLMWrapper(llm)
        self._ragas_embeddings = LangchainEmbeddingsWrapper(embeddings)

    def provider_name(self) -> str:
        """Return the provider identifier."""
        return "ragas"

    def supported_metrics(self) -> Sequence[str]:
        """Return metrics supported by the RAGAS provider."""
        return list(self._METRIC_MAP.keys())

    def _build_dataset_and_metrics(
        self,
        request: EvaluationRequest,
    ) -> tuple[Dataset, list[Metric]]:
        """Construct evaluation dataset and selected RAGAS metrics."""
        data: dict[str, list[Any]] = {
            "user_input": [request.question],
            "response": [request.answer],
            "retrieved_contexts": [request.contexts],
        }

        has_ground_truth = bool(
            request.ground_truth and request.ground_truth.strip()
        )

        if has_ground_truth:
            data["reference"] = [request.ground_truth]

        dataset = Dataset.from_dict(data)

        if request.metric_config:
            requested = {
                metric.metric_name
                for metric in request.metric_config
                if metric.enabled and metric.metric_name in self._METRIC_MAP
            }
        else:
            requested = set(self._METRIC_MAP)

        selected_metrics: list[Metric] = []

        for name in sorted(requested):
            if (
                name in _REFERENCE_REQUIRED_METRICS
                and not has_ground_truth
            ):
                continue

            selected_metrics.append(self._METRIC_MAP[name])

        if not selected_metrics:
            raise ValueError(
                "No valid metrics available for evaluation."
            )

        return dataset, selected_metrics

    @staticmethod
    def _sanitize_score(value: Any) -> float:
        """Convert a raw RAGAS score into a normalized float."""
        if isinstance(value, (list, tuple)):
            value = value[0] if value else 0.0

        try:
            score = float(value)
            if math.isnan(score):
                return 0.0
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(1.0, score))

    def evaluate(self, request: EvaluationRequest) -> dict[str, float]:
        """Execute synchronous RAGAS evaluation using shared Groq LLM and embeddings."""
        dataset, selected_metrics = self._build_dataset_and_metrics(request)

        try:
            result = evaluate(
                dataset=dataset,
                metrics=selected_metrics,
                llm=self._ragas_llm,
                embeddings=self._ragas_embeddings,
            )
        except Exception as exc:
            raise ValueError(
                f"RAGAS evaluation failed: {exc}"
            ) from exc

        scores: dict[str, float] = {}

        for metric in selected_metrics:
            try:
                raw = result[metric.name]
            except (KeyError, TypeError, IndexError):
                raw = 0.0

            scores[metric.name] = self._sanitize_score(raw)

        return scores

    async def evaluate_async(
        self,
        request: EvaluationRequest,
    ) -> dict[str, float]:
        """Execute asynchronous RAGAS evaluation."""
        return self.evaluate(request)