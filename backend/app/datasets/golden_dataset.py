"""
Golden Dataset Data Primitives.

Defines sample data structures, ground truth containers, and validation rules for
RAG evaluation benchmark datasets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class GoldenSample:
    """Dataclass representing a single golden dataset evaluation sample.

    Attributes:
        sample_id (str): Unique sample identifier UUID.
        query (str): Input question or user prompt.
        expected_output (Optional[str]): Ground truth reference output.
        contexts (List[str]): Reference contexts or ground truth documents.
        actual_output (Optional[str]): System generated output under test.
        retrieved_contexts (List[str]): Contexts retrieved by RAG system under test.
        metadata (Dict[str, Any]): Sample metadata (domain, tags, difficulty, etc.).
    """

    query: str
    sample_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    expected_output: Optional[str] = None
    contexts: List[str] = field(default_factory=list)
    actual_output: Optional[str] = None
    retrieved_contexts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class GoldenDataset:
    """Container for managing collections of GoldenSample test cases."""

    def __init__(
        self,
        dataset_id: str,
        name: str,
        description: str = "",
        samples: Optional[List[GoldenSample]] = None,
    ) -> None:
        """Initialize GoldenDataset container.

        Args:
            dataset_id (str): Unique identifier for dataset.
            name (str): Human readable dataset name.
            description (str): Detailed description of test set.
            samples (Optional[List[GoldenSample]]): Initial samples list.
        """
        self.dataset_id = dataset_id
        self.name = name
        self.description = description
        self.samples: List[GoldenSample] = samples or []

    def add_sample(self, sample: GoldenSample) -> None:
        """Add a single golden sample to dataset.

        Args:
            sample (GoldenSample): Golden sample instance.
        """
        self.samples.append(sample)

    def get_sample(self, sample_id: str) -> Optional[GoldenSample]:
        """Retrieve golden sample by sample_id.

        Args:
            sample_id (str): Sample UUID string.

        Returns:
            Optional[GoldenSample]: Found sample or None.
        """
        for sample in self.samples:
            if sample.sample_id == sample_id:
                return sample
        return None

    def filter_by_tag(self, tag: str) -> List[GoldenSample]:
        """Filter dataset samples containing a specific tag in metadata.

        Args:
            tag (str): Target tag string.

        Returns:
            List[GoldenSample]: Filtered list of samples.
        """
        return [
            s for s in self.samples if tag in s.metadata.get("tags", [])
        ]

    def validate(self) -> bool:
        """Validate dataset structure ensuring non-empty queries.

        Returns:
            bool: True if valid dataset, False otherwise.
        """
        if not self.samples:
            return False
        return all(bool(s.query.strip()) for s in self.samples)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataset into dictionary format.

        Returns:
            Dict[str, Any]: Dictionary representation of dataset.
        """
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "description": self.description,
            "samples_count": len(self.samples),
        }
