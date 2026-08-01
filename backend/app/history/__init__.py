"""
Evaluation History Package.

Provides persistence repositories and query managers for evaluation run history,
trend analysis, and result retrieval.
"""

from backend.app.history.evaluation_history import (
    BaseEvaluationHistoryRepository,
    EvaluationHistoryManager,
    EvaluationRecord,
)

__all__ = [
    "EvaluationRecord",
    "BaseEvaluationHistoryRepository",
    "EvaluationHistoryManager",
]
