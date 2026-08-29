from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ProjectInfo(BaseModel):
    project_name: str
    domain: str
    scale: str
    budget: str
    deployment_target: str
    optimization_priority: str


class ArchitectureRationale(BaseModel):
    category: str
    recommended: str
    reason: str

class ArchitectureDetails(BaseModel):
    components: Dict[str, str]
    decision_signals: Dict[str, str]
    rationale: List[ArchitectureRationale]

class ArchitectureReport(BaseModel):
    id: str
    title: str
    generated_at: str
    project_profile: ProjectInfo
    architecture: ArchitectureDetails

class ReportGenerationRequest(BaseModel):
    decision_result: Optional[Dict[str, Any]] = None
    benchmark_result: Optional[Dict[str, Any]] = None
    evaluation_result: Optional[Dict[str, Any]] = None
