"""Explanation engine module for generating deterministic architectural recommendation rationale."""

from app.schemas.decision import RecommendationItem


class ExplanationEngine:
    """Engine responsible for synthesizing human-readable explanation strings for recommendations."""

    @staticmethod
    def _build_reason(item: RecommendationItem) -> str:
        """Construct detailed explanation rationale for a RecommendationItem."""
        base_reason = (
            f"Selected {item.recommended} because it achieved the highest overall score "
            f"for the '{item.category}' category after applying project constraints and priority weighting."
        )

        if item.alternatives:
            alt_str = ", ".join(item.alternatives)
            base_reason += f" Alternative options considered: {alt_str}."

        return base_reason

    def generate(
        self, recommendations: list[RecommendationItem]
    ) -> list[RecommendationItem]:
        """Generate enhanced deterministic explanations for architectural recommendations."""
        enhanced_recommendations: list[RecommendationItem] = []

        for item in recommendations:
            new_reason = self._build_reason(item)
            enhanced_item = RecommendationItem(
                category=item.category,
                recommended=item.recommended,
                confidence=item.confidence,
                reason=new_reason,
                alternatives=list(item.alternatives),
            )
            enhanced_recommendations.append(enhanced_item)

        return enhanced_recommendations
