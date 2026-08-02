"""Unit tests for Phase 3.2 Requirement Understanding Engine."""

from app.decision.domain_detector import Domain
from app.decision.requirement_analyzer import (
    BudgetTier,
    DocScaleTier,
    RequirementAnalyzer,
    ScaleTier,
)
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


def test_five_projects_produce_different_project_profiles():
    """Verify that five distinct project requests produce 5 distinct, correctly classified ProjectProfiles."""
    # 1. Research Project
    req_research = DecisionRequest(
        project_name="Academic Paper RAG",
        project_description="Academic literature search tool for scientific journal papers with citation verification.",
        expected_users=250,
        document_count=50_000,
        budget_usd=100.0,
        deployment_target=DeploymentTarget.GCP,
        priority=Priority.QUALITY,
        constraints=["citation support", "academic references"],
    )

    # 2. Enterprise Project
    req_enterprise = DecisionRequest(
        project_name="Corporate Knowledge Vault",
        project_description="Internal company employee portal with SOC2 security compliance, SSO authentication, and SLA guarantees.",
        expected_users=250_000,
        document_count=5_000_000,
        budget_usd=20_000.0,
        deployment_target=DeploymentTarget.AWS,
        priority=Priority.QUALITY,
        constraints=["SOC2 compliance", "enterprise security", "high availability"],
    )

    # 3. Healthcare Project
    req_healthcare = DecisionRequest(
        project_name="Clinical Patient Assistant",
        project_description="Clinical medical decision support for doctor hospital patient EHR records requiring HIPAA compliance.",
        expected_users=1_500,
        document_count=100_000,
        budget_usd=1_500.0,
        deployment_target=DeploymentTarget.ON_PREM,
        priority=Priority.QUALITY,
        constraints=["HIPAA compliance", "on-premise privacy"],
    )

    # 4. Education Chatbot
    req_education = DecisionRequest(
        project_name="University Student Tutor",
        project_description="Interactive student course learning tutor for online university grade prep.",
        expected_users=8_000,
        document_count=5_000,
        budget_usd=50.0,
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.COST,
        constraints=["free tier", "open-source required"],
    )

    # 5. Developer Documentation Assistant
    req_dev_tools = DecisionRequest(
        project_name="GitHub Code Search CLI",
        project_description="Developer CLI tool searching code repositories, SDKs, and API documentation for refactoring.",
        expected_users=45_000,
        document_count=500_000,
        budget_usd=500.0,
        deployment_target=DeploymentTarget.LOCAL,
        priority=Priority.LATENCY,
        constraints=["fast sub-100ms latency", "local execution"],
    )

    profile1 = RequirementAnalyzer.analyze(req_research)
    profile2 = RequirementAnalyzer.analyze(req_enterprise)
    profile3 = RequirementAnalyzer.analyze(req_healthcare)
    profile4 = RequirementAnalyzer.analyze(req_education)
    profile5 = RequirementAnalyzer.analyze(req_dev_tools)

    # Assert all 5 profiles produce distinct domains
    domains = {p.domain for p in (profile1, profile2, profile3, profile4, profile5)}
    assert len(domains) == 5
    assert profile1.domain == Domain.RESEARCH
    assert profile2.domain == Domain.ENTERPRISE
    assert profile3.domain == Domain.HEALTHCARE
    assert profile4.domain == Domain.EDUCATION
    assert profile5.domain == Domain.DEVELOPER_TOOLS

    # Assert scale tiers
    assert profile1.project_scale == ScaleTier.SMALL
    assert profile2.project_scale == ScaleTier.ENTERPRISE
    assert profile3.project_scale == ScaleTier.MEDIUM
    assert profile4.project_scale == ScaleTier.MEDIUM
    assert profile5.project_scale == ScaleTier.LARGE

    # Assert document scale tiers
    assert profile1.document_scale == DocScaleTier.MEDIUM
    assert profile2.document_scale == DocScaleTier.MASSIVE
    assert profile3.document_scale == DocScaleTier.LARGE
    assert profile4.document_scale == DocScaleTier.SMALL
    assert profile5.document_scale == DocScaleTier.LARGE

    # Assert budget tiers
    assert profile1.budget_tier == BudgetTier.FREE_LOW
    assert profile2.budget_tier == BudgetTier.HIGH_UNLIMITED
    assert profile3.budget_tier == BudgetTier.MEDIUM
    assert profile4.budget_tier == BudgetTier.FREE_LOW
    assert profile5.budget_tier == BudgetTier.MEDIUM

    # Assert constraint flags
    assert profile1.requires_citations is True
    assert profile2.requires_enterprise_security is True
    assert profile3.requires_privacy is True
    assert profile4.requires_open_source is True
    assert profile5.requires_low_latency is True

    print("\n--- FIVE PROJECT PROFILES VERIFIED DISTINCTLY ---")
    for idx, p in enumerate([profile1, profile2, profile3, profile4, profile5], 1):
        print(f"Project {idx} ({p.project_name}): Domain={p.domain.value}, Scale={p.project_scale.value}, DocScale={p.document_scale.value}, BudgetTier={p.budget_tier.value}")


if __name__ == "__main__":
    test_five_projects_produce_different_project_profiles()
