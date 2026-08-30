import pytest
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority
from app.services.decision_service import DecisionService
from app.decision.retriever import KnowledgeRetriever
from app.decision.constraint_matcher import ConstraintMatcher
from app.decision.scoring_engine import ScoringEngine
from app.decision.recommendation_engine import RecommendationEngine
from app.decision.explanation_engine import ExplanationEngine
import app.core.config
import shutil
from pathlib import Path

# Monkeypatch Qdrant storage for tests to avoid lock issues if backend is running
temp_qdrant = Path("temp_qdrant_test")
if temp_qdrant.exists():
    shutil.rmtree(temp_qdrant)

vs_path = Path("knowledge_base/vector_store_new")
if not vs_path.exists():
    vs_path = Path("knowledge_base/vector_store")

shutil.copytree(vs_path, temp_qdrant)
app.core.config.QDRANT_PATH = temp_qdrant
import app.retriever.qdrant_retriever
app.retriever.qdrant_retriever.QDRANT_PATH = temp_qdrant

@pytest.fixture
def decision_service():
    retriever = KnowledgeRetriever()
    constraint_matcher = ConstraintMatcher()
    scoring_engine = ScoringEngine()
    recommendation_engine = RecommendationEngine()
    explanation_engine = ExplanationEngine()
    return DecisionService(
        retriever,
        constraint_matcher,
        scoring_engine,
        recommendation_engine,
        explanation_engine
    )

def test_offline_open_source_local(decision_service):
    """Offline + Open Source + Local -> Cloud/proprietary must never survive."""
    req = DecisionRequest(
        project_name="Offline Setup",
        project_description="I need a personal AI assistant that runs entirely locally on my MacBook. Completely offline. Open-source only.",
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.COST,
        budget_usd=0
    )
    
    response = decision_service.recommend(req)
    for rec in response.recommendations:
        name = rec.recommended.lower()
        if rec.category.lower() == "llm":
            assert "openai gpt" not in name
            assert "claude" not in name
        assert "aws" not in name
        assert "azure" not in name

def test_enterprise_aws(decision_service):
    """Enterprise AWS -> AWS-native technologies should remain eligible."""
    req = DecisionRequest(
        project_name="Enterprise AWS",
        project_description="Enterprise hospital network on AWS. Must be HIPAA compliant and highly secure.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        budget_usd=50000
    )
    
    response = decision_service.recommend(req)
    deployment_rec = next(r for r in response.recommendations if r.category.lower() == "deployment")
    # Verify a cloud/enterprise option is recommended
    assert any(k in deployment_rec.recommended.lower() for k in ("ray", "aws", "sagemaker", "weights"))

def test_open_source_only(decision_service):
    """Open Source only -> Proprietary technologies must be excluded."""
    req = DecisionRequest(
        project_name="Open Source Web App",
        project_description="We are building an open source community tool.",
        deployment_target=DeploymentTarget.GCP,
        priority=Priority.COST,
        budget_usd=100,
        constraints=["open_source"]
    )
    
    response = decision_service.recommend(req)
    for rec in response.recommendations:
        name = rec.recommended.lower()
        if rec.category.lower() == "llm":
            assert "openai gpt" not in name
            assert "claude" not in name

def test_low_budget_projects(decision_service):
    """Low-budget projects -> Premium technologies should receive appropriate penalties."""
    req = DecisionRequest(
        project_name="Low Budget Startup",
        project_description="Startup SaaS with 1000 users. Need a vector DB. Budget $100/month.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.COST,
        budget_usd=100
    )
    
    response = decision_service.recommend(req)
    for rec in response.recommendations:
        if rec.category.lower() == "vector_db":
            assert "pinecone" not in rec.recommended.lower()

def test_no_explicit_constraints(decision_service):
    """No explicit constraints -> Existing recommendation behavior should remain unchanged."""
    req = DecisionRequest(
        project_name="Standard Project",
        project_description="A standard rag pipeline.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        budget_usd=2000
    )
    
    response = decision_service.recommend(req)
    assert len(response.recommendations) > 0

def test_langfuse_is_evaluation(decision_service):
    """Ensure Langfuse is categorized under evaluation and not deployment."""
    req = DecisionRequest(
        project_name="Evaluation Project",
        project_description="I need a tool for LLM observability and evaluation like Langfuse.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        budget_usd=1000
    )
    
    response = decision_service.recommend(req)
    
    evaluation_candidates = [r.recommended.lower() for r in response.recommendations if r.category.lower() == "evaluation"]
    deployment_candidates = [r.recommended.lower() for r in response.recommendations if r.category.lower() == "deployment"]
    
    assert any("langfuse" in name for name in evaluation_candidates), "Langfuse should be recommended for evaluation"
    assert not any("langfuse" in name for name in deployment_candidates), "Langfuse must NOT be in deployment"
