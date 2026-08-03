"""Domain detection module inferring project domains from natural language descriptions."""

from enum import Enum
from typing import Dict, List, Set


class Domain(str, Enum):
    """Supported project domains."""

    RESEARCH = "research"
    ENTERPRISE = "enterprise"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    FINANCE = "finance"
    STARTUP = "startup"
    EDUCATION = "education"
    ECOMMERCE = "ecommerce"
    CUSTOMER_SUPPORT = "customer_support"
    DEVELOPER_TOOLS = "developer_tools"
    GENERAL = "general"


_DOMAIN_KEYWORDS: Dict[Domain, List[str]] = {
    Domain.RESEARCH: [
        "research", "academic", "paper", "scientific", "study", "experiment",
        "citation", "hypothesis", "benchmark", "thesis", "dataset", "ragas"
    ],
    Domain.ENTERPRISE: [
        "enterprise", "corporate", "multi-tenant", "soc2", "compliance",
        "high availability", "sla", "scale", "sso", "rbac", "audit log"
    ],
    Domain.HEALTHCARE: [
        "medical", "patient", "clinical", "hipaa", "health", "hospital",
        "doctor", "pharma", "ehr", "diagnosis"
    ],
    Domain.LEGAL: [
        "legal", "law", "contract", "statute", "court", "attorney",
        "litigation", "paralegal", "clause", "agreement"
    ],
    Domain.FINANCE: [
        "finance", "financial", "banking", "trading", "fintech", "stock",
        "fraud", "portfolio", "sec", "payment", "ledger"
    ],
    Domain.STARTUP: [
        "startup", "mvp", "bootstrap", "prototype", "indie", "side project",
        "lean", "early-stage", "free tier", "offline assistant"
    ],
    Domain.EDUCATION: [
        "education", "school", "student", "learning", "course", "university",
        "teacher", "tutor", "curriculum", "grade"
    ],
    Domain.ECOMMERCE: [
        "ecommerce", "e-commerce", "store", "product catalog", "checkout",
        "retail", "shopping", "cart", "merchant"
    ],
    Domain.CUSTOMER_SUPPORT: [
        "customer support", "helpdesk", "support ticket", "customer service",
        "agent", "chatbot", "faq", "resolution"
    ],
    Domain.DEVELOPER_TOOLS: [
        "developer", "code", "github", "ide", "cli", "sdk", "compiler",
        "api", "repo", "git", "refactoring", "linter"
    ],
}


class DomainDetector:
    """Detector responsible for classifying project descriptions into domain categories."""

    @classmethod
    def detect(cls, description: str) -> Domain:
        """Infer the primary Domain of a project description based on keyword density."""
        if not description or not description.strip():
            return Domain.GENERAL

        text_lower = description.lower()
        domain_scores: Dict[Domain, int] = {d: 0 for d in _DOMAIN_KEYWORDS}

        for domain, keywords in _DOMAIN_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    domain_scores[domain] += 1

        best_domain = max(domain_scores, key=lambda d: domain_scores[d])
        if domain_scores[best_domain] > 0:
            return best_domain

        return Domain.GENERAL
