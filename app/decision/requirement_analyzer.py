"""Requirement Understanding Engine module converting raw project requests into structured ProjectProfiles."""

from dataclasses import dataclass, field
from enum import Enum
import logging
import re
from typing import List, Optional

from app.decision.domain_detector import Domain, DomainDetector
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority

logger = logging.getLogger(__name__)

def _parse_number_with_multiplier(match_str: str) -> int:
    """Parse string like '5 million', '5M', '100k', '5000000' into integer."""
    s = match_str.lower().replace(',', '')
    multiplier = 1
    if 'm' in s or 'million' in s:
        multiplier = 1_000_000
    elif 'b' in s or 'billion' in s:
        multiplier = 1_000_000_000
    elif 'k' in s or 'thousand' in s:
        multiplier = 1_000
    
    num_match = re.search(r'[\d\.]+', s)
    if not num_match:
        return 0
    return int(float(num_match.group()) * multiplier)

class ScaleTier(str, Enum):
    """User scale classification tiers."""

    TINY = "tiny"          # <100 users
    SMALL = "small"        # 100 - 1k users
    MEDIUM = "medium"      # 1k - 10k users
    LARGE = "large"        # 10k - 100k users
    ENTERPRISE = "enterprise"  # 100k+ users


class DocScaleTier(str, Enum):
    """Document scale classification tiers."""

    TINY = "tiny"          # <1k docs
    SMALL = "small"        # 1k - 10k docs
    MEDIUM = "medium"      # 10k - 100k docs
    LARGE = "large"        # 100k - 1M docs
    MASSIVE = "massive"    # 1M+ docs


class BudgetTier(str, Enum):
    """Monthly budget classification tiers."""

    FREE_LOW = "free_low"            # <= $200 USD/mo
    MEDIUM = "medium"                # $200 - $2,000 USD/mo
    HIGH_UNLIMITED = "high_unlimited"  # > $2,000 USD/mo or unconstrained


@dataclass
class ProjectProfile:
    """Structured internal representation of analyzed project requirements."""

    project_name: str
    project_description: str
    domain: Domain
    deployment: DeploymentTarget
    project_scale: ScaleTier
    document_scale: DocScaleTier
    budget_tier: BudgetTier
    priority: Priority
    quality_priority: float
    cost_priority: float
    latency_priority: float
    expected_scale: int
    document_count: int
    budget_usd: Optional[float]
    requires_open_source: bool
    requires_local_execution: bool
    requires_privacy: bool
    requires_low_latency: bool
    requires_citations: bool
    requires_gpu: bool
    requires_enterprise_security: bool
    requires_high_availability: bool
    preferred_llm: Optional[str] = None
    preferred_vector_db: Optional[str] = None
    preferred_framework: Optional[str] = None
    constraints: List[str] = field(default_factory=list)


class RequirementAnalyzer:
    """Requirement Understanding Engine converting raw requests into structured ProjectProfiles."""

    @classmethod
    def _classify_user_scale(cls, users: int) -> ScaleTier:
        """Classify expected user count into ScaleTier."""
        if users < 100:
            return ScaleTier.TINY
        if users < 1_000:
            return ScaleTier.SMALL
        if users < 10_000:
            return ScaleTier.MEDIUM
        if users < 100_000:
            return ScaleTier.LARGE
        return ScaleTier.ENTERPRISE

    @classmethod
    def _classify_doc_scale(cls, docs: int) -> DocScaleTier:
        """Classify document count into DocScaleTier."""
        if docs < 1_000:
            return DocScaleTier.TINY
        if docs < 10_000:
            return DocScaleTier.SMALL
        if docs < 100_000:
            return DocScaleTier.MEDIUM
        if docs < 1_000_000:
            return DocScaleTier.LARGE
        return DocScaleTier.MASSIVE

    @classmethod
    def _classify_budget_tier(cls, budget: Optional[float], priority: Priority) -> BudgetTier:
        """Classify monthly budget into BudgetTier combining budget_usd and priority."""
        if budget is None:
            return BudgetTier.HIGH_UNLIMITED if priority != Priority.COST else BudgetTier.MEDIUM
        if budget <= 200.0:
            return BudgetTier.FREE_LOW
        if budget <= 2_000.0:
            return BudgetTier.MEDIUM
        return BudgetTier.HIGH_UNLIMITED

    @classmethod
    def analyze(cls, request: DecisionRequest) -> ProjectProfile:
        """Parse, classify, and infer structured ProjectProfile from raw DecisionRequest."""
        desc = request.project_description.lower()

        users = request.expected_users or 0
        if users == 0:
            user_match = re.search(r'([\d\.,]+(?:\s*(?:m|b|k|million|billion|thousand))?)\s*(?:\w+\s*){0,3}(?:users|customers|active users)', desc)
            if user_match:
                users = _parse_number_with_multiplier(user_match.group(1))

        docs = request.document_count or 0
        if docs == 0:
            doc_match = re.search(r'([\d\.,]+(?:\s*(?:m|b|k|million|billion|thousand))?)\s*(?:\w+\s*){0,3}(?:documents|docs|records)', desc)
            if doc_match:
                docs = _parse_number_with_multiplier(doc_match.group(1))

        budget = request.budget_usd
        if budget is None or budget == 0:
            budget_match = re.search(r'(?:\$([\d\.,]+(?:k|m)?)|([\d\.,]+(?:k|m)?)\s*(?:usd|dollars)|budget\s+([\d\.,]+(?:k|m)?))', desc)
            if budget_match:
                b_str = budget_match.group(1) or budget_match.group(2) or budget_match.group(3)
                budget = float(_parse_number_with_multiplier(b_str))

        # 1. Infer Domain
        domain = DomainDetector.detect(request.project_description)

        # 2. Scale Classifications
        project_scale = cls._classify_user_scale(users)
        document_scale = cls._classify_doc_scale(docs)

        # 3. Budget Classification
        budget_tier = cls._classify_budget_tier(budget, request.priority)

        # 4. Priority Weight Allocations
        quality_weight = 0.25
        cost_weight = 0.25
        latency_weight = 0.25

        if request.priority == Priority.QUALITY:
            quality_weight, cost_weight, latency_weight = 0.55, 0.20, 0.25
        elif request.priority == Priority.COST:
            quality_weight, cost_weight, latency_weight = 0.20, 0.55, 0.25
        elif request.priority == Priority.LATENCY:
            quality_weight, cost_weight, latency_weight = 0.25, 0.20, 0.55

        # 5. Free-Text & Structural Constraint Detection
        constraints_lower = [c.lower() for c in request.constraints]
        all_text = (request.project_description.lower() + " " + " ".join(constraints_lower)).strip()

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
            or bool(re.search(r'\d+\s*ms', all_text))
        )
        requires_privacy = (
            requires_local_execution
            or any(kw in all_text for kw in ("privacy", "gdpr", "hipaa", "security", "isolated"))
        )
        requires_citations = (
            domain == Domain.RESEARCH
            or any(kw in all_text for kw in ("citation", "ragas", "reference", "academic", "journal", "thesis"))
        )
        requires_gpu = any(
            kw in all_text for kw in ("gpu", "cuda", "vllm", "triton", "tensorrt", "h100", "a100")
        )
        requires_enterprise_security = (
            domain in (Domain.ENTERPRISE, Domain.FINANCE, Domain.HEALTHCARE)
            or request.deployment_target in (DeploymentTarget.AWS, DeploymentTarget.AZURE)
            or any(kw in all_text for kw in ("soc2", "compliance", "security", "sla", "sso", "rbac", "hipaa"))
        )
        requires_high_availability = (
            project_scale in (ScaleTier.LARGE, ScaleTier.ENTERPRISE)
            or any(kw in all_text for kw in ("high availability", "ha", "multi-region", "failover", "99.99"))
        )

        # 6. Preferred Component Parsing
        pref_llm = request.preferred_llm.strip() if request.preferred_llm and request.preferred_llm.strip() else None
        pref_vdb = None
        pref_framework = None

        for kw in ("qdrant", "pinecone", "chroma", "milvus", "weaviate", "faiss"):
            if kw in all_text:
                pref_vdb = kw.capitalize()
                break

        for kw in ("langchain", "llamaindex", "haystack", "dspy", "autogen"):
            if kw in all_text:
                pref_framework = kw.capitalize()
                break

        unified_constraints = set(c.strip().lower() for c in request.constraints if c and c.strip())
        if requires_open_source: unified_constraints.add("open_source")
        if requires_local_execution: unified_constraints.add("local_execution")
        if requires_privacy: unified_constraints.add("privacy")
        if requires_low_latency: unified_constraints.add("low_latency")
        if requires_citations: unified_constraints.add("citations")
        if requires_gpu: unified_constraints.add("gpu")
        if requires_enterprise_security: unified_constraints.add("enterprise_security")
        if requires_high_availability: unified_constraints.add("high_availability")

        profile = ProjectProfile(
            project_name=request.project_name,
            project_description=request.project_description,
            domain=domain,
            deployment=request.deployment_target,
            project_scale=project_scale,
            document_scale=document_scale,
            budget_tier=budget_tier,
            priority=request.priority,
            quality_priority=quality_weight,
            cost_priority=cost_weight,
            latency_priority=latency_weight,
            expected_scale=users,
            document_count=docs,
            budget_usd=budget,
            requires_open_source=requires_open_source,
            requires_local_execution=requires_local_execution,
            requires_privacy=requires_privacy,
            requires_low_latency=requires_low_latency,
            requires_citations=requires_citations,
            requires_gpu=requires_gpu,
            requires_enterprise_security=requires_enterprise_security,
            requires_high_availability=requires_high_availability,
            preferred_llm=pref_llm,
            preferred_vector_db=pref_vdb,
            preferred_framework=pref_framework,
            constraints=list(unified_constraints),
        )

        # 7. Development & Pipeline Structured INFO Logging
        detected_constraints_list = []
        if requires_open_source: detected_constraints_list.append("open_source")
        if requires_local_execution: detected_constraints_list.append("local_execution")
        if requires_privacy: detected_constraints_list.append("privacy")
        if requires_low_latency: detected_constraints_list.append("low_latency")
        if requires_citations: detected_constraints_list.append("citations")
        if requires_gpu: detected_constraints_list.append("gpu")
        if requires_enterprise_security: detected_constraints_list.append("enterprise_security")
        if requires_high_availability: detected_constraints_list.append("high_availability")

        inferred_prefs = []
        if pref_llm: inferred_prefs.append(f"Preferred LLM: {pref_llm}")
        if pref_vdb: inferred_prefs.append(f"Preferred Vector DB: {pref_vdb}")
        if pref_framework: inferred_prefs.append(f"Preferred Framework: {pref_framework}")

        logger.info("=================== PROJECT PROFILE ANALYZED ===================")
        logger.info(f"Project Name        : {profile.project_name}")
        logger.info(f"Domain              : {profile.domain.value}")
        logger.info(f"User Scale          : {profile.project_scale.value} ({users:,} users)")
        logger.info(f"Document Scale      : {profile.document_scale.value} ({docs:,} docs)")
        logger.info(f"Budget Tier         : {profile.budget_tier.value} (${budget or 0:,.2f}/mo)")
        logger.info(f"Deployment Target   : {profile.deployment.value}")
        logger.info(f"Priority            : {profile.priority.value}")
        logger.info(f"Detected Constraints: {', '.join(detected_constraints_list) if detected_constraints_list else 'None'}")
        logger.info(f"Inferred Preferences: {', '.join(inferred_prefs) if inferred_prefs else 'None'}")
        logger.info(f"Full ProjectProfile : {profile}")
        logger.info("================================================================")

        return profile
