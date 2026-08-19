from typing import List, Optional
from pydantic import BaseModel, Field

class KnowledgeCategoryCount(BaseModel):
    name: str
    count: int
    label: str

class KnowledgeComponent(BaseModel):
    id: str
    category: str
    name: str
    organization: Optional[str] = None
    officialDocumentation: Optional[str] = None
    githubRepository: Optional[str] = None
    license: Optional[str] = None
    priority: Optional[str] = None
    lastVerified: Optional[str] = None
    description: Optional[str] = None
    keyFeatures: List[str] = Field(default_factory=list)

class KnowledgeRegistryResponse(BaseModel):
    totalComponents: int
    lastSync: str
    categories: List[KnowledgeCategoryCount]
    components: List[KnowledgeComponent]
    page: int
    page_size: int
    total_pages: int
