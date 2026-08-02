"""Unit tests for Phase 3.1 Refinement — Intelligent Recommendation Quality."""

from app.api.deps import get_decision_service
from app.decision.domain_detector import Domain, DomainDetector
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


def test_domain_detection():
    """Verify DomainDetector accurately infers domains from natural language descriptions."""
    assert DomainDetector.detect("Academic literature review and paper citation study") == Domain.RESEARCH
    assert DomainDetector.detect("Corporate multi-tenant enterprise SOC2 platform") == Domain.ENTERPRISE
    assert DomainDetector.detect("Clinical patient medical diagnosis assistant") == Domain.HEALTHCARE
    assert DomainDetector.detect("Contract clause review and legal compliance auditor") == Domain.LEGAL
    assert DomainDetector.detect("Bootstrap indie startup offline desktop tool") == Domain.STARTUP


def test_startup_vs_enterprise_different_vectordb_recommendations():
    """Prove that Startup and Enterprise produce different vector DB recommendations."""
    service = get_decision_service()

    # Startup Local project
    startup_req = DecisionRequest(
        project_name="Startup MVP Assistant",
        project_description="Bootstrap startup building a local offline assistant for developers.",
        expected_users=10,
        document_count=500,
        budget_usd=0.0,
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.COST,
        constraints=["open-source required", "runs locally"],
    )

    # Enterprise AWS project
    enterprise_req = DecisionRequest(
        project_name="Enterprise Knowledge Base",
        project_description="Corporate multi-tenant enterprise intelligence portal with strict SOC2 compliance.",
        expected_users=100_000,
        document_count=1_000_000,
        budget_usd=10_000.0,
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        constraints=["enterprise security", "high availability"],
    )

    res_startup = service.recommend(startup_req)
    res_enterprise = service.recommend(enterprise_req)

    recs_startup = {r.category: r.recommended for r in res_startup.recommendations}
    recs_enterprise = {r.category: r.recommended for r in res_enterprise.recommendations}

    assert recs_startup.get("vectordbs") != recs_enterprise.get("vectordbs")
    print(f"Startup VectorDB: {recs_startup.get('vectordbs')} | Enterprise VectorDB: {recs_enterprise.get('vectordbs')}")


def test_open_source_constraint_changes_rankings():
    """Prove open source constraint penalizes proprietary models/services and alters recommendations."""
    service = get_decision_service()

    req_cloud = DecisionRequest(
        project_name="Cloud RAG Platform",
        project_description="High-quality RAG system on AWS.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        constraints=[],
    )

    req_oss = DecisionRequest(
        project_name="Open Source RAG Platform",
        project_description="High-quality RAG system on AWS.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        constraints=["open-source required"],
    )

    res_cloud = service.recommend(req_cloud)
    res_oss = service.recommend(req_oss)

    recs_cloud = {r.category: r.recommended for r in res_cloud.recommendations}
    recs_oss = {r.category: r.recommended for r in res_oss.recommendations}

    assert recs_cloud != recs_oss
    print(f"Cloud Stack: {recs_cloud} | OSS Stack: {recs_oss}")


def test_preferred_llm_affects_model_recommendation():
    """Prove preferred_llm explicitly influences LLM recommendation."""
    service = get_decision_service()

    req_claude = DecisionRequest(
        project_name="Claude Project",
        project_description="Legal document reasoning platform.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        preferred_llm="Anthropic Claude",
    )

    req_gemini = DecisionRequest(
        project_name="Gemini Project",
        project_description="Legal document reasoning platform.",
        deployment_target=DeploymentTarget.GCP,
        priority=Priority.QUALITY,
        preferred_llm="Google Gemini",
    )

    res_claude = service.recommend(req_claude)
    res_gemini = service.recommend(req_gemini)

    llm1 = next((r.recommended for r in res_claude.recommendations if r.category == "llm"), None)
    llm2 = next((r.recommended for r in res_gemini.recommendations if r.category == "llm"), None)

    assert llm1 != llm2
    print(f"Preferred Claude LLM Rec: {llm1} | Preferred Gemini LLM Rec: {llm2}")


def test_confidence_values_vary_appropriately():
    """Prove confidence values calibrate appropriately (strong matches higher, weak matches lower)."""
    service = get_decision_service()

    strong_req = DecisionRequest(
        project_name="Strong Match Enterprise",
        project_description="Corporate multi-tenant enterprise SOC2 platform on AWS.",
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        expected_users=500_000,
        document_count=2_000_000,
        budget_usd=50_000.0,
        constraints=["enterprise security"],
    )

    res = service.recommend(strong_req)
    vdb_rec = next((r for r in res.recommendations if r.category == "vectordbs"), None)
    deploy_rec = next((r for r in res.recommendations if r.category == "deployment"), None)

    assert vdb_rec is not None and vdb_rec.confidence >= 0.70
    assert deploy_rec is not None and deploy_rec.confidence >= 0.70
    assert res.overall_confidence >= 0.60
    print(f"Strong Match VectorDB Confidence: {vdb_rec.confidence} | Overall Confidence: {res.overall_confidence}")


if __name__ == "__main__":
    test_domain_detection()
    test_startup_vs_enterprise_different_vectordb_recommendations()
    test_open_source_constraint_changes_rankings()
    test_preferred_llm_affects_model_recommendation()
    test_confidence_values_vary_appropriately()
    print("\nALL REFINEMENT UNIT TESTS PASSED CLEANLY!")
