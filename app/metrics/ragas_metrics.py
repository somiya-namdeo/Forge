"""RAGAS metric evaluator provider implementation."""

from collections.abc import Sequence
import math

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

from app.core.config import EMBEDDING_MODEL, GROQ_API_KEY, LLM_MODEL
from app.metrics.base import BaseMetricEvaluator
from app.schemas.evaluation import EvaluationRequest

_REFERENCE_REQUIRED_METRICS = {"context_precision", "context_recall"}


class RagasEvaluator(BaseMetricEvaluator):
    """RAGAS evaluation framework provider implementing BaseMetricEvaluator."""

    def __init__(self) -> None:
        """Initialize RAGAS evaluator with Groq LLM and BGE embeddings."""
        self._llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.0,
        )
        self._ragas_llm = LangchainLLMWrapper(self._llm)
        self._embeddings = HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL)
        self._ragas_embeddings = LangchainEmbeddingsWrapper(self._embeddings)
        self._all_metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

    @property
    def provider_name(self) -> str:
        """Return unique provider identifier."""
        return "ragas"

    @property
    def supported_metrics(self) -> Sequence[str]:
        """Return sequence of metrics supported by RAGAS provider."""
        return ("faithfulness", "answer_relevancy", "context_precision", "context_recall")

    def evaluate(self, request: EvaluationRequest) -> dict[str, float]:
        """Evaluate a single RAG response using RAGAS framework metrics."""
        has_ground_truth = bool(request.ground_truth and request.ground_truth.strip())

        if has_ground_truth:
            eval_metrics = self._all_metrics
        else:
            eval_metrics = [m for m in self._all_metrics if m.name not in _REFERENCE_REQUIRED_METRICS]

        dataset_dict = {
            "question": [request.question],
            "answer": [request.answer],
            "contexts": [request.contexts if request.contexts else [""]],
        }
        if has_ground_truth:
            dataset_dict["ground_truth"] = [request.ground_truth]
            dataset_dict["reference"] = [request.ground_truth]

        dataset = Dataset.from_dict(dataset_dict)

        results = evaluate(
            dataset=dataset,
            metrics=eval_metrics,
            llm=self._ragas_llm,
            embeddings=self._ragas_embeddings,
            raise_exceptions=False,
        )

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

            if raw_val is None or (isinstance(raw_val, float) and math.isnan(raw_val)):
                scores[m_name] = 0.0
            else:
                scores[m_name] = min(1.0, max(0.0, float(raw_val)))

        return scores
