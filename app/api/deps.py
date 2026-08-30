"""FastAPI dependency providers for Forge application."""

from functools import lru_cache

from fastapi import Depends

from app.decision.constraint_matcher import ConstraintMatcher
from app.decision.explanation_engine import ExplanationEngine
from app.decision.recommendation_engine import RecommendationEngine
from app.decision.retriever import KnowledgeRetriever
from app.decision.scoring_engine import ScoringEngine
from app.metrics.ragas_metrics import RagasEvaluator
from app.metrics.registry import MetricRegistry
from app.services.decision_service import DecisionService
from app.services.evaluation_service import EvaluationService
from app.thresholds.threshold_manager import ThresholdManager
from app.utils.weighting import WeightingEngine


@lru_cache
def get_metric_registry() -> MetricRegistry:
    """Provide a singleton MetricRegistry populated with default evaluation providers."""
    registry = MetricRegistry()
    registry.register(RagasEvaluator())
    return registry


@lru_cache
def get_weighting_engine() -> WeightingEngine:
    """Provide a singleton WeightingEngine instance."""
    return WeightingEngine()


@lru_cache
def get_threshold_manager() -> ThresholdManager:
    """Provide a singleton ThresholdManager instance."""
    return ThresholdManager()


def get_evaluation_service(
    registry: MetricRegistry | None = Depends(get_metric_registry),
    weighting_engine: WeightingEngine | None = Depends(get_weighting_engine),
    threshold_manager: ThresholdManager | None = Depends(get_threshold_manager),
) -> EvaluationService:
    """Inject dependencies into EvaluationService for route handlers or direct calls."""
    if hasattr(registry, "dependency") or registry is None:
        registry = get_metric_registry()
    if hasattr(weighting_engine, "dependency") or weighting_engine is None:
        weighting_engine = get_weighting_engine()
    if hasattr(threshold_manager, "dependency") or threshold_manager is None:
        threshold_manager = get_threshold_manager()

    return EvaluationService(
        metric_registry=registry,
        weighting_engine=weighting_engine,
        threshold_manager=threshold_manager,
    )







@lru_cache
def get_knowledge_retriever() -> KnowledgeRetriever:
    """Provide a singleton KnowledgeRetriever instance."""
    return KnowledgeRetriever()


@lru_cache
def get_constraint_matcher() -> ConstraintMatcher:
    """Provide a singleton ConstraintMatcher instance."""
    return ConstraintMatcher()


@lru_cache
def get_scoring_engine() -> ScoringEngine:
    """Provide a singleton ScoringEngine instance."""
    return ScoringEngine()


@lru_cache
def get_recommendation_engine() -> RecommendationEngine:
    """Provide a singleton RecommendationEngine instance."""
    return RecommendationEngine()


@lru_cache
def get_explanation_engine() -> ExplanationEngine:
    """Provide a singleton ExplanationEngine instance."""
    return ExplanationEngine()


def get_decision_service(
    retriever: KnowledgeRetriever | None = Depends(get_knowledge_retriever),
    constraint_matcher: ConstraintMatcher | None = Depends(get_constraint_matcher),
    scoring_engine: ScoringEngine | None = Depends(get_scoring_engine),
    recommendation_engine: RecommendationEngine | None = Depends(get_recommendation_engine),
    explanation_engine: ExplanationEngine | None = Depends(get_explanation_engine),
) -> DecisionService:
    """Inject dependencies into DecisionService for route handlers or direct calls."""
    if hasattr(retriever, "dependency") or retriever is None:
        retriever = get_knowledge_retriever()
    if hasattr(constraint_matcher, "dependency") or constraint_matcher is None:
        constraint_matcher = get_constraint_matcher()
    if hasattr(scoring_engine, "dependency") or scoring_engine is None:
        scoring_engine = get_scoring_engine()
    if hasattr(recommendation_engine, "dependency") or recommendation_engine is None:
        recommendation_engine = get_recommendation_engine()
    if hasattr(explanation_engine, "dependency") or explanation_engine is None:
        explanation_engine = get_explanation_engine()

    return DecisionService(
        retriever=retriever,
        constraint_matcher=constraint_matcher,
        scoring_engine=scoring_engine,
        recommendation_engine=recommendation_engine,
        explanation_engine=explanation_engine,
    )



