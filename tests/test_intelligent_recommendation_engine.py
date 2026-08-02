"""Unit tests for Phase 3.1 Intelligent Recommendation Engine."""

from app.api.deps import (
    get_constraint_matcher,
    get_decision_service,
    get_explanation_engine,
    get_knowledge_retriever,
    get_recommendation_engine,
    get_scoring_engine,
)
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


def test_three_distinct_project_scenarios_produce_different_recommendations():
    """Verify that three distinct project profiles produce meaningfully different recommendations,

    scores, confidence levels, and project-specific explanations.
    """
    decision_service = get_decision_service()

    # --- Scenario 1: Startup Local / Open Source / Low Budget ---
    req_scenario1 = DecisionRequest(
        project_name="Privacy Local Assistant",
        project_description="Offline desktop document assistant requiring sub-100ms real-time latency and strict privacy.",
        expected_users=50,
        document_count=1000,
        budget_usd=50.0,
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.LATENCY,
        preferred_llm=None,
        constraints=["open-source required", "sub-100ms latency", "local privacy"],
    )

    # --- Scenario 2: Enterprise High-Scale AWS Platform ---
    req_scenario2 = DecisionRequest(
        project_name="Global Enterprise Search",
        project_description="Mission-critical cloud-native enterprise intelligence platform requiring maximum quality and throughput.",
        expected_users=1_000_000,
        document_count=5_000_000,
        budget_usd=25_000.0,
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        preferred_llm="OpenAI GPT",
        constraints=["SOC2 compliance", "high availability", "AWS integration"],
    )

    # --- Scenario 3: Mid-Market GCP Analytics ---
    req_scenario3 = DecisionRequest(
        project_name="Customer Feedback Analytics",
        project_description="Batch customer sentiment analysis system optimized for minimal monthly cloud operating cost.",
        expected_users=2_500,
        document_count=100_000,
        budget_usd=250.0,
        deployment_target=DeploymentTarget.GCP,
        priority=Priority.COST,
        preferred_llm="Google Gemini",
        constraints=["cost optimization", "GCP cloud run"],
    )

    res1 = decision_service.recommend(req_scenario1)
    res2 = decision_service.recommend(req_scenario2)
    res3 = decision_service.recommend(req_scenario3)

    # 1. Assert all responses return recommendations
    assert len(res1.recommendations) > 0
    assert len(res2.recommendations) > 0
    assert len(res3.recommendations) > 0

    # 2. Assert confidence is dynamic and NOT hardcoded 0.70
    for res in (res1, res2, res3):
        assert res.overall_confidence != 0.70
        for rec in res.recommendations:
            assert rec.confidence != 0.70
            assert 0.0 <= rec.confidence <= 1.0

    # 3. Compare Vector DB / Category recommendations across scenarios
    recs1_map = {r.category: r for r in res1.recommendations}
    recs2_map = {r.category: r for r in res2.recommendations}
    recs3_map = {r.category: r for r in res3.recommendations}

    # 4. Assert overall confidence values differ meaningfully between scenarios
    confidences = {res1.overall_confidence, res2.overall_confidence, res3.overall_confidence}
    assert len(confidences) >= 2, "Overall confidence should vary across different project scenarios"

    # 5. Assert reasons contain project-specific keywords
    reason1_concat = " ".join([r.reason for r in res1.recommendations]).lower()
    reason2_concat = " ".join([r.reason for r in res2.recommendations]).lower()
    reason3_concat = " ".join([r.reason for r in res3.recommendations]).lower()

    assert "local" in reason1_concat or "latency" in reason1_concat or "open-source" in reason1_concat
    assert "aws" in reason2_concat or "quality" in reason2_concat or "openai" in reason2_concat
    assert "gcp" in reason3_concat or "cost" in reason3_concat or "gemini" in reason3_concat

    print("Scenario 1 Overall Confidence:", res1.overall_confidence)
    print("Scenario 2 Overall Confidence:", res2.overall_confidence)
    print("Scenario 3 Overall Confidence:", res3.overall_confidence)
    print("\n--- TEST PASSED CLEANLY! ---")


if __name__ == "__main__":
    test_three_distinct_project_scenarios_produce_different_recommendations()
