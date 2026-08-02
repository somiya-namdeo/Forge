from app.knowledge_builder.models import (
    TechnologyMetadata,
    PerformanceMetadata,
    PricingMetadata,
    AdoptionMetadata,
    CapabilityMetadata,
    RecommendationMetadata,
)

from app.knowledge_builder.parser import MetadataParser
from app.knowledge_builder.validator import MetadataValidator


class MetadataExtractor:

    def extract(
        self,
        technology_name: str,
        category: str,
        chunks: list[dict],
    ) -> TechnologyMetadata:

        parser = MetadataParser(chunks)

        metadata = TechnologyMetadata(

            technology=technology_name,

            category=category,

            description=parser.all_text()[:500],

            aliases=[],

            tags=parser.extract_tags(),

            performance=PerformanceMetadata(),

            pricing=PricingMetadata(
                license=parser.license(),
            ),

            adoption=AdoptionMetadata(),

            capabilities=CapabilityMetadata(
                supported_deployments=[],
                supported_languages=[],
                features=parser.extract_features(),
            ),

            recommendation=RecommendationMetadata(),
        )

        return MetadataValidator.validate(metadata)