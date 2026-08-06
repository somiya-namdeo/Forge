from pydantic import BaseModel, Field
from app.schemas.decision import DecisionRequest, RecommendationItem

class DecisionRunRequest(BaseModel):
    request: DecisionRequest = Field(..., description="The original decision request")
    recommendations: list[RecommendationItem] = Field(..., description="The ranked recommendations from the Recommendation Engine")
