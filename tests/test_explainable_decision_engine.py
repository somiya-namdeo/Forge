"""Unit tests for Phase 3.3 Explainable Decision Engine."""

from app.api.deps import get_decision_service
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


def test_explainable_decision_engine_output():
    """Verify Phase 3.3 explainability attributes on RecommendationItem and DecisionResponse."""
    service = get_decision_service()

    req = DecisionRequest(
        project_name="Explainable Azure Platform",
        project_description="Enterprise legal search platform with citation support and SOC2 compliance.",
        expected_users=50_000,
        document_count=800_000,
        budget_usd=2_500.0,
        deployment_target=DeploymentTarget.AZURE,
        priority=Priority.QUALITY,
        preferred_llm="Anthropic Claude",
        constraints=["citation support", "enterprise security"],
    )

    res = service.recommend(req)

    # 1. Pipeline Statistics Assertions
    stats = res.pipeline_statistics
    assert stats is not None
    assert "technologies_considered" in stats and stats["technologies_considered"] > 0
    assert "categories_processed" in stats and stats["categories_processed"] > 0
    assert "average_confidence" in stats and 0.0 <= stats["average_confidence"] <= 1.0
    assert "retrieval_time_ms" in stats
    assert "ranking_time_ms" in stats
    print("Pipeline Statistics Verified:", stats)

    # 2. RecommendationItem Explainability Attribute Assertions
    assert len(res.recommendations) > 0

    for item in res.recommendations:
        # A. Score Breakdown
        sb = item.score_breakdown
        assert isinstance(sb, dict)
        for key in (
            "deployment_fit", "constraint_match", "domain_fit", "metadata_quality",
            "documentation_quality", "cost_efficiency", "throughput_scalability", "overall"
        ):
            assert key in sb, f"Missing score breakdown key '{key}' in category '{item.category}'"
            assert 0.0 <= sb[key] <= 1.0

        # B. Decision Trace
        dt = item.decision_trace
        assert isinstance(dt, list) and len(dt) >= 4
        assert any("Deployment target:" in trace for trace in dt)
        assert any("Priority:" in trace for trace in dt)

        # C. Evidence Metadata
        ev = item.evidence
        assert isinstance(ev, dict)
        assert "technology_id" in ev
        assert "organization" in ev
        assert "license" in ev
        assert "source" in ev
        assert "url" in ev

        # D. Alternative Analysis
        aa = item.alternative_analysis
        assert isinstance(aa, list)
        for alt in aa:
            assert hasattr(alt, "name") and len(alt.name) > 0
            assert hasattr(alt, "reason") and len(alt.reason) > 0

        # E. Confidence Level
        cl = item.confidence_level
        assert cl in ("Very High", "High", "Medium", "Low", "Weak")

        # F. Metadata Used
        mu = item.metadata_used
        assert isinstance(mu, list) and len(mu) >= 5

    # Print sample recommendation item explainability payload
    sample_item = res.recommendations[0]
    print("\n--- SAMPLE EXPLAINABLE RECOMMENDATION ITEM ---")
    print("Category        :", sample_item.category)
    print("Recommended     :", sample_item.recommended)
    print("Confidence      :", sample_item.confidence, f"({sample_item.confidence_level})")
    print("Score Breakdown :", sample_item.score_breakdown)
    print("Decision Trace  :", sample_item.decision_trace)
    print("Evidence        :", sample_item.evidence)
    print("Alternatives    :", [f"{a.name}: {a.reason}" for a in sample_item.alternative_analysis])
    print("Metadata Used   :", sample_item.metadata_used)
    print("----------------------------------------------")


if __name__ == "__main__":
    test_explainable_decision_engine_output()
    print("\nALL EXPLAINABLE DECISION ENGINE TESTS PASSED CLEANLY!")
