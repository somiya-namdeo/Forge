"""Requirement extraction module for AI Architecture Recommendation Engine."""

from dataclasses import dataclass, field
from typing import List, Optional

from app.decision.domain_detector import Domain, DomainDetector
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority


@dataclass
class RequirementProfile:
    """Structured requirement profile extracted from DecisionRequest."""

    project_name: str
    project_description: str
    deployment_target: DeploymentTarget
    priority: Priority
    domain: Domain = Domain.GENERAL
    expected_users: int = 0
    document_count: int = 0
    budget_usd: Optional[float] = None
    preferred_llm: Optional[str] = None
    constraints: List[str] = field(default_factory=list)

    # Derived requirement attributes & constraint signals
    is_high_scale: bool = False
    is_medium_scale: bool = False
    is_low_budget: bool = False
    is_unlimited_budget: bool = False
    requires_open_source: bool = False
    requires_low_latency: bool = False
    requires_privacy: bool = False
    requires_citation_support: bool = False
    requires_enterprise_security: bool = False
    requires_high_accuracy: bool = False
    requires_local_execution: bool = False
    normalized_preferred_llm: Optional[str] = None


class RequirementExtractor:
    """Extractor responsible for parsing DecisionRequest into a RequirementProfile."""

    @staticmethod
    def extract(request: DecisionRequest) -> RequirementProfile:
        """Extract structured profile features and domain signals from a DecisionRequest."""
        users = request.expected_users or 0
        docs = request.document_count or 0
        budget = request.budget_usd

        domain = DomainDetector.detect(request.project_description)

        is_high_scale = users >= 100_000 or docs >= 500_000
        is_medium_scale = (1_000 <= users < 100_000) or (10_000 <= docs < 500_000)

        is_low_budget = budget is not None and budget <= 200.0
        is_unlimited_budget = budget is None or budget >= 10_000.0

        constraints_lower = [c.lower() for c in request.constraints]
        desc_lower = request.project_description.lower()
        all_text = desc_lower + " " + " ".join(constraints_lower)

        requires_open_source = any(
            kw in all_text
            for kw in ("open source", "open-source", "oss", "self-hosted", "local assistant")
        )
        requires_local_execution = (
            request.deployment_target in (DeploymentTarget.LOCAL, DeploymentTarget.ON_PREM)
            or any(kw in all_text for kw in ("local", "offline", "on-prem", "air-gapped"))
        )
        requires_low_latency = (
            request.priority == Priority.LATENCY
            or any(kw in all_text for kw in ("latency", "realtime", "real-time", "fast", "<100ms", "sub-100ms"))
        )
        requires_privacy = (
            requires_local_execution
            or any(kw in all_text for kw in ("privacy", "gdpr", "hipaa", "security", "isolated"))
        )
        requires_citation_support = (
            domain == Domain.RESEARCH
            or any(kw in all_text for kw in ("citation", "ragas", "reference", "academic", "thesis", "evaluation"))
        )
        requires_enterprise_security = (
            domain in (Domain.ENTERPRISE, Domain.FINANCE, Domain.HEALTHCARE)
            or request.deployment_target in (DeploymentTarget.AWS, DeploymentTarget.AZURE)
            or any(kw in all_text for kw in ("soc2", "compliance", "security", "sla", "enterprise"))
        )
        requires_high_accuracy = (
            request.priority == Priority.QUALITY
            or domain in (Domain.LEGAL, Domain.HEALTHCARE, Domain.FINANCE)
            or any(kw in all_text for kw in ("accuracy", "rerank", "sota", "precision", "high accuracy"))
        )

        pref_llm = None
        if request.preferred_llm and request.preferred_llm.strip():
            pref_llm = request.preferred_llm.strip().lower()

        return RequirementProfile(
            project_name=request.project_name,
            project_description=request.project_description,
            deployment_target=request.deployment_target,
            priority=request.priority,
            domain=domain,
            expected_users=users,
            document_count=docs,
            budget_usd=budget,
            preferred_llm=request.preferred_llm,
            constraints=request.constraints,
            is_high_scale=is_high_scale,
            is_medium_scale=is_medium_scale,
            is_low_budget=is_low_budget,
            is_unlimited_budget=is_unlimited_budget,
            requires_open_source=requires_open_source,
            requires_low_latency=requires_low_latency,
            requires_privacy=requires_privacy,
            requires_citation_support=requires_citation_support,
            requires_enterprise_security=requires_enterprise_security,
            requires_high_accuracy=requires_high_accuracy,
            requires_local_execution=requires_local_execution,
            normalized_preferred_llm=pref_llm,
        )
