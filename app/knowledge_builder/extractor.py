from pathlib import Path
import json
import re

from app.knowledge_builder.models import (
    CapabilityMetadata,
    PricingMetadata,
    TechnologyMetadata,
)
from app.knowledge_builder.normalizer import Normalizer
from app.knowledge_builder.validator import MetadataValidator

_LANGUAGE_PATTERNS = {
    "Python": re.compile(r"\bpython\b", re.IGNORECASE),
    "JavaScript": re.compile(r"\bjavascript\b", re.IGNORECASE),
    "TypeScript": re.compile(r"\btypescript\b", re.IGNORECASE),
    "Java": re.compile(r"\bjava\b", re.IGNORECASE),
    "Go": re.compile(r"\bgo(lang)?\b", re.IGNORECASE),
    "Rust": re.compile(r"\brust\b", re.IGNORECASE),
    "C++": re.compile(r"\bc\+\+\b", re.IGNORECASE),
    "C#": re.compile(r"\bc#\b|csharp", re.IGNORECASE),
    "PHP": re.compile(r"\bphp\b", re.IGNORECASE),
    "Ruby": re.compile(r"\bruby\b", re.IGNORECASE),
    "Swift": re.compile(r"\bswift\b", re.IGNORECASE),
    "Kotlin": re.compile(r"\bkotlin\b", re.IGNORECASE),
}

_DEPLOYMENT_PATTERNS = {
    "aws": re.compile(r"\baws\b|\bamazon web services\b", re.IGNORECASE),
    "azure": re.compile(r"\bazure\b|\bmicrosoft azure\b", re.IGNORECASE),
    "gcp": re.compile(r"\bgcp\b|\bgoogle cloud\b|\bgoogle cloud platform\b", re.IGNORECASE),
    "docker": re.compile(r"\bdocker\b", re.IGNORECASE),
    "kubernetes": re.compile(r"\bkubernetes\b|\bk8s\b", re.IGNORECASE),
    "local": re.compile(r"\blocal\b", re.IGNORECASE),
    "on_prem": re.compile(r"\bon[- ]?prem\b|\bon[- ]?premise\b|\bon[- ]?premises\b", re.IGNORECASE),
    "serverless": re.compile(r"\bserverless\b", re.IGNORECASE),
}

_LICENSE_PATTERNS = {
    "MIT": re.compile(r"\bmit license\b|\bmit\b", re.IGNORECASE),
    "Apache-2.0": re.compile(r"\bapache[- ]?2(\.0)?\b|\bapache license\b", re.IGNORECASE),
    "GPLv3": re.compile(r"\bgpl[- ]?3(\.0)?\b|\bgplv3\b", re.IGNORECASE),
    "GPL": re.compile(r"\bgpl\b", re.IGNORECASE),
    "BSD": re.compile(r"\bbsd\b", re.IGNORECASE),
    "MPL": re.compile(r"\bmozilla public license\b|\bmpl\b", re.IGNORECASE),
}

_FEATURE_PATTERNS = {
    "RAG": re.compile(r"\brag\b|\bretrieval augmented generation\b", re.IGNORECASE),
    "Agents": re.compile(r"\bagent\b|\bagents\b", re.IGNORECASE),
    "Embeddings": re.compile(r"\bembedding\b|\bembeddings\b", re.IGNORECASE),
    "Vector Search": re.compile(r"\bvector search\b", re.IGNORECASE),
    "Hybrid Search": re.compile(r"\bhybrid search\b", re.IGNORECASE),
    "Semantic Search": re.compile(r"\bsemantic search\b", re.IGNORECASE),
    "Reranking": re.compile(r"\brerank\b|\breranker\b|\breranking\b", re.IGNORECASE),
    "Tool Calling": re.compile(r"\btool calling\b", re.IGNORECASE),
    "Function Calling": re.compile(r"\bfunction calling\b", re.IGNORECASE),
    "Streaming": re.compile(r"\bstreaming\b", re.IGNORECASE),
    "Fine Tuning": re.compile(r"\bfine[- ]?tuning\b|\bfine tuning\b", re.IGNORECASE),
    "Quantization": re.compile(r"\bquantization\b|\bquantisation\b", re.IGNORECASE),
    "Multimodal": re.compile(r"\bmultimodal\b", re.IGNORECASE),
    "Evaluation": re.compile(r"\bevaluation\b|\bevaluate\b", re.IGNORECASE),
    "Observability": re.compile(r"\bobservability\b|\btracing\b", re.IGNORECASE),
    "Memory": re.compile(r"\bmemory\b", re.IGNORECASE),
    "Caching": re.compile(r"\bcache\b|\bcaching\b", re.IGNORECASE),
    "Prompt Engineering": re.compile(r"\bprompt\b", re.IGNORECASE),
}


class MetadataExtractor:
    def __init__(self) -> None:
        self.normalizer = Normalizer()
        self.validator = MetadataValidator()

    def _load_documents(self, technology_dir: Path) -> list[dict]:
        documents = []
        if not technology_dir.exists() or not technology_dir.is_dir():
            return documents

        for file_path in sorted(technology_dir.rglob("*.json")):
            try:
                with file_path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue

            if isinstance(data, dict):
                if "content" in data and str(data["content"]).strip():
                    documents.append(data)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "content" in item and str(item["content"]).strip():
                        documents.append(item)

        return documents

    def _merge_documents(self, documents: list[dict]) -> tuple[str, dict[str, str]]:
        source_texts: dict[str, list[str]] = {}
        merged_blocks = []

        for document in documents:
            content = str(document.get("content", "")).strip()
            if not content:
                continue

            source = str(document.get("source", "unknown")).strip().lower()
            source_texts.setdefault(source, []).append(content)
            merged_blocks.append(content)

        sources = {source: "\n\n".join(texts) for source, texts in source_texts.items()}
        return "\n\n".join(merged_blocks), sources

    def _truncate_description(self, text: str, max_chars: int = 650) -> str:
        if len(text) <= max_chars:
            return text

        cutoff = text[:max_chars]
        last_space = cutoff.rfind(" ")
        if last_space > 200:
            cutoff = cutoff[:last_space]

        return cutoff.rstrip(".,;:- ") + "..."

    def _extract_description(self, sources: dict[str, str], merged_text: str) -> str | None:
        priority = (
            "official_documentation",
            "official_docs",
            "documentation",
            "github_repository",
            "readme",
            "technical_blog",
        )

        target_text = ""
        for source in priority:
            if source in sources:
                target_text = sources[source]
                break

        if not target_text:
            target_text = merged_text

        target_text = target_text.replace("\r", "")
        for block in target_text.split("\n\n"):
            paragraph = " ".join(block.split()).strip()
            if not paragraph or paragraph.startswith(("#", "=", "-", "*", "```", "~~~", "`")):
                continue

            if len(paragraph) < 40:
                continue

            return self._truncate_description(paragraph)

        return None

    def _match_patterns(self, pattern_map: dict[str, re.Pattern], text: str) -> list[str]:
        return [key for key, pattern in pattern_map.items() if pattern.search(text)]

    def _extract_languages(self, text: str) -> list[str]:
        matches = self._match_patterns(_LANGUAGE_PATTERNS, text)
        return self.normalizer.normalize_list(matches)

    def _extract_deployments(self, text: str) -> list[str]:
        matches = self._match_patterns(_DEPLOYMENT_PATTERNS, text)
        normalized = [self.normalizer.normalize_deployment(item) or item for item in matches]
        return self.normalizer.normalize_list(normalized)

    def _extract_license(self, text: str) -> str | None:
        for license_name, pattern in _LICENSE_PATTERNS.items():
            if pattern.search(text):
                return self.normalizer.normalize_license(license_name)
        return None

    def _extract_open_source(self, text: str, license_name: str | None) -> bool | None:
        if license_name is not None:
            return True

        lower = text.lower()
        if any(keyword in lower for keyword in ("open source", "opensource", "oss", "source available", "community edition")):
            return True

        if any(keyword in lower for keyword in ("proprietary", "closed source", "commercial only")):
            return False

        return None

    def _extract_free_tier(self, text: str) -> bool | None:
        lower = text.lower()
        keywords = (
            "free tier",
            "free plan",
            "free forever",
            "freemium",
            "trial available",
            "no cost",
            "community edition",
        )
        if any(keyword in lower for keyword in keywords):
            return True

        if "no free tier" in lower or "paid only" in lower:
            return False

        return None

    def _extract_features(self, text: str) -> list[str]:
        matches = self._match_patterns(_FEATURE_PATTERNS, text)
        return self.normalizer.normalize_list(matches)

    def _extract_aliases(self, technology: str) -> list[str]:
        aliases = {technology}
        cleaned = technology.replace("_", " ").replace("-", " ")
        words = cleaned.split()

        aliases.add(cleaned)
        aliases.add("-".join(words))

        if len(words) > 1:
            aliases.add(" ".join(words))
            aliases.add("".join(words))

        return sorted(self.normalizer.normalize_list(list(aliases)))

    def _extract_tags(self, capabilities: CapabilityMetadata, pricing: PricingMetadata) -> list[str]:
        tags = []
        tags.extend(capabilities.supported_languages)
        tags.extend(capabilities.supported_deployments)
        tags.extend(capabilities.features)

        if pricing.license:
            tags.append(pricing.license)
        if pricing.open_source:
            tags.append("Open Source")
        if pricing.free_tier:
            tags.append("Free Tier")

        return self.normalizer.normalize_list(tags)

    def _build_metadata(
        self, technology: str, category: str, merged_text: str, sources: dict[str, str]
    ) -> TechnologyMetadata:
        license_name = self._extract_license(merged_text)
        open_source = self._extract_open_source(merged_text, license_name)
        free_tier = self._extract_free_tier(merged_text)
        description = self._extract_description(sources, merged_text)
        aliases = self._extract_aliases(technology)

        capabilities = CapabilityMetadata(
            supported_languages=self._extract_languages(merged_text),
            supported_deployments=self._extract_deployments(merged_text),
            features=self._extract_features(merged_text),
        )
        pricing = PricingMetadata(
            license=license_name,
            open_source=open_source,
            free_tier=free_tier,
        )
        tags = self._extract_tags(capabilities, pricing)

        metadata = TechnologyMetadata(
            technology=technology,
            category=category,
            description=description,
            aliases=aliases,
            capabilities=capabilities,
            pricing=pricing,
            tags=tags,
        )

        return self.validator.validate(metadata)

    def extract(self, technology_dir: Path, category: str) -> TechnologyMetadata | None:
        documents = self._load_documents(technology_dir)
        if not documents:
            return None

        merged_text, sources = self._merge_documents(documents)
        technology = documents[0].get("technology") or technology_dir.name
        technology = self.normalizer.normalize_text(technology) or technology_dir.name

        return self._build_metadata(
            technology=technology, category=category, merged_text=merged_text, sources=sources
        )