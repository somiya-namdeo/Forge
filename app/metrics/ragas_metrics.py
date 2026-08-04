"""RAGAS metric evaluator provider implementation."""

from collections.abc import Sequence
import math
from typing import Any

from datasets import Dataset
from langchain_openai import ChatOpenAI
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
)

from app.core.config import (
    EVALUATION_API_KEY,
    EVALUATION_MODEL,
    EVALUATION_PROVIDER,
)
from app.embeddings.embedding_service import get_embedding_model
from app.metrics.base import BaseMetricEvaluator
from app.schemas.evaluation import EvaluationRequest

import time
import logging

logger = logging.getLogger(__name__)


_ragas_evaluator_instance = None


def get_ragas_evaluator() -> "RagasEvaluator":
    """Return singleton instance of RagasEvaluator to avoid model re-initialization."""
    global _ragas_evaluator_instance
    if _ragas_evaluator_instance is None:
        _ragas_evaluator_instance = RagasEvaluator()
    return _ragas_evaluator_instance


class RagasEvaluator(BaseMetricEvaluator):
    """RAGAS evaluation framework provider implementing BaseMetricEvaluator.

    Maintains singletons for LLM and Embeddings wrappers, ensuring high performance
    and zero model re-initialization during repeated evaluations. Includes a 60s provider
    circuit breaker on rate limits / timeouts.
    """

    _circuit_breaker_until: float = 0.0

    @classmethod
    def is_circuit_open(cls) -> bool:
        """Return True if circuit breaker is currently open (cooling down)."""
        return time.time() < cls._circuit_breaker_until

    @classmethod
    def trip_circuit_breaker(cls, cooldown_seconds: float = 60.0) -> None:
        """Trip circuit breaker for cooldown_seconds on 429/timeout/provider failures."""
        cls._circuit_breaker_until = time.time() + cooldown_seconds
        logger.info("RAGAS circuit breaker TRIP OPEN (60s cooldown initiated).")

    @classmethod
    def reset_circuit_breaker(cls) -> None:
        """Reset circuit breaker state (for testing)."""
        cls._circuit_breaker_until = 0.0

    def __init__(self) -> None:
        """Initialize RAGAS evaluator with Evaluation Groq account LLM and BGE embeddings wrappers."""
        self._llm = ChatOpenAI(
            model=EVALUATION_MODEL,
            api_key=EVALUATION_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.0,
            max_retries=0,
            request_timeout=5.0,
        )
        self._ragas_llm = LangchainLLMWrapper(self._llm)
        self._embeddings = get_embedding_model()
        self._ragas_embeddings = LangchainEmbeddingsWrapper(self._embeddings)

        self._metric_map = {
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
        }

    @property
    def provider_name(self) -> str:
        """Return unique provider identifier."""
        return "ragas"

    @property
    def supported_metrics(self) -> Sequence[str]:
        """Return sequence of metrics supported by RAGAS provider."""
        return tuple(self._metric_map.keys())

    def _resolve_requested_metrics(self, request: EvaluationRequest) -> list[Any]:
        """Resolve enabled metrics based on request metric_config."""
        if request.metric_config:
            enabled_names = set()
            for cfg in request.metric_config:
                if hasattr(cfg, "metric_type"):
                    m_val = getattr(cfg.metric_type, "value", str(cfg.metric_type))
                elif hasattr(cfg, "value"):
                    m_val = cfg.value
                else:
                    m_val = str(cfg)
                m_clean = m_val.lower().strip()
                if m_clean == "answer_relevance":
                    m_clean = "answer_relevancy"
                enabled_names.add(m_clean)

            selected_metrics = [
                m_obj
                for name, m_obj in self._metric_map.items()
                if name in enabled_names
            ]
        else:
            selected_metrics = list(self._metric_map.values())

        return selected_metrics

    def evaluate(self, request: EvaluationRequest) -> dict[str, float]:
        """Evaluate a single RAG response using RAGAS framework metrics.

        Args:
            request (EvaluationRequest): Evaluation input request.

        Returns:
            dict[str, float]: Dictionary mapping metric names to normalized scores.

        Raises:
            ValueError: If RAGAS evaluation fails or circuit breaker is open.
        """
        if self.is_circuit_open():
            cooldown_rem = int(self._circuit_breaker_until - time.time())
            logger.info("RAGAS circuit breaker OPEN (%ds cooldown remaining). Skipping provider call.", max(1, cooldown_rem))
            raise ValueError(f"RAGAS circuit breaker OPEN ({cooldown_rem}s remaining on 429/timeout cooldown)")

        eval_metrics = self._resolve_requested_metrics(request)
        if not eval_metrics:
            return {}

        has_ground_truth = bool(request.ground_truth and request.ground_truth.strip())
        contexts_list = request.contexts if request.contexts else [""]

        dataset_dict: dict[str, list[Any]] = {
            "user_input": [request.question],
            "question": [request.question],
            "response": [request.answer],
            "answer": [request.answer],
            "retrieved_contexts": [contexts_list],
            "contexts": [contexts_list],
        }
        if has_ground_truth:
            dataset_dict["reference"] = [request.ground_truth]
            dataset_dict["ground_truth"] = [request.ground_truth]

        try:
            dataset = Dataset.from_dict(dataset_dict)
            run_config = RunConfig(
                max_workers=1,
                max_retries=0,
                timeout=10,
            )
            results = evaluate(
                dataset=dataset,
                metrics=eval_metrics,
                llm=self._ragas_llm,
                embeddings=self._ragas_embeddings,
                run_config=run_config,
                raise_exceptions=True,
            )
        except Exception as exc:
            self.trip_circuit_breaker(60.0)
            metric_names = [getattr(m, "name", str(m)) for m in eval_metrics]
            raise ValueError(
                f"RAGAS evaluation failed for metrics {metric_names}: {exc}"
            ) from exc

        scores: dict[str, float] = {}
        for metric in eval_metrics:
            m_name = getattr(metric, "name", str(metric))
            raw_val = None

            try:
                raw_val = results[m_name]
            except (KeyError, TypeError, AttributeError):
                pass

            if raw_val is None and hasattr(results, m_name):
                raw_val = getattr(results, m_name)

            if isinstance(raw_val, (list, tuple)):
                if len(raw_val) > 0 and raw_val[0] is not None:
                    raw_val = sum(raw_val) / len(raw_val)
                else:
                    raw_val = 0.0

            if raw_val is None or not isinstance(raw_val, (int, float)) or math.isnan(raw_val):
                scores[m_name] = 0.0
            else:
                scores[m_name] = min(1.0, max(0.0, float(raw_val)))

        return scores
