"""
Evaluation History Module.

Defines historical record schemas and repository interfaces for recording, querying,
and auditing evaluation execution runs over time.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from app.metrics import PassFailStatus


@dataclass
class EvaluationRecord:
    """Dataclass storing historical evaluation run data.

    Attributes:
        evaluation_id (str): Unique evaluation UUID.
        rag_architecture_id (str): ID of RAG architecture recommendation evaluated.
        dataset_id (str): Benchmark dataset ID used.
        composite_score (float): Final composite evaluation score.
        overall_status (PassFailStatus): PASS, FAIL, or WARNING status.
        timestamp (datetime): Timestamp when evaluation was executed.
        metrics_summary (Dict[str, float]): Aggregated metric scores map.
        metadata (Dict[str, Any]): Additional execution parameters or notes.
    """

    rag_architecture_id: str
    dataset_id: str
    composite_score: float
    overall_status: PassFailStatus
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metrics_summary: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseEvaluationHistoryRepository(ABC):
    """Abstract repository for persisting and searching evaluation history."""

    @abstractmethod
    def save(self, record: EvaluationRecord) -> EvaluationRecord:
        """Save an evaluation run record to history.

        Args:
            record (EvaluationRecord): Historical record object.

        Returns:
            EvaluationRecord: Saved evaluation record.
        """

    @abstractmethod
    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationRecord]:
        """Get evaluation record by evaluation_id.

        Args:
            evaluation_id (str): Evaluation UUID string.

        Returns:
            Optional[EvaluationRecord]: Found record or None.
        """

    @abstractmethod
    def search(
        self,
        rag_architecture_id: Optional[str] = None,
        status: Optional[PassFailStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[EvaluationRecord]:
        """Search and filter historical evaluation records.

        Args:
            rag_architecture_id (Optional[str]): Filter by architecture ID.
            status (Optional[PassFailStatus]): Filter by pass/fail status.
            limit (int): Maximum records to return.
            offset (int): Pagination offset.

        Returns:
            List[EvaluationRecord]: Matching evaluation records.
        """


class EvaluationHistoryManager(BaseEvaluationHistoryRepository):
    """In-memory reference implementation of evaluation history repository."""

    def __init__(self) -> None:
        """Initialize in-memory history storage."""
        self._history: Dict[str, EvaluationRecord] = {}

    def save(self, record: EvaluationRecord) -> EvaluationRecord:
        """Save evaluation record in memory.

        Args:
            record (EvaluationRecord): Record instance.

        Returns:
            EvaluationRecord: Saved record.
        """
        self._history[record.evaluation_id] = record
        return record

    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationRecord]:
        """Retrieve evaluation record by ID.

        Args:
            evaluation_id (str): Evaluation ID.

        Returns:
            Optional[EvaluationRecord]: Found record or None.
        """
        return self._history.get(evaluation_id)

    def search(
        self,
        rag_architecture_id: Optional[str] = None,
        status: Optional[PassFailStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[EvaluationRecord]:
        """Search and filter in-memory evaluation records.

        Args:
            rag_architecture_id (Optional[str]): Architecture ID.
            status (Optional[PassFailStatus]): Pass/Fail status filter.
            limit (int): Max count.
            offset (int): Pagination offset.

        Returns:
            List[EvaluationRecord]: Filtered evaluation records list.
        """
        records = list(self._history.values())
        if rag_architecture_id:
            records = [r for r in records if r.rag_architecture_id == rag_architecture_id]
        if status:
            records = [r for r in records if r.overall_status == status]
        return records[offset : offset + limit]

    def delete(self, evaluation_id: str) -> bool:
        """Delete an evaluation record by ID.

        Args:
            evaluation_id (str): Evaluation ID.

        Returns:
            bool: True if deleted, False if not found.
        """
        if evaluation_id in self._history:
            del self._history[evaluation_id]
            return True
        return False
