"""
Benchmark Loader Module.

Provides abstract and concrete loaders for importing golden datasets from local files
(JSON, CSV) or remote benchmark sources (HuggingFace, custom endpoints).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.app.datasets.golden_dataset import GoldenDataset, GoldenSample


class BenchmarkLoader(ABC):
    """Abstract interface for dataset loading implementations."""

    @abstractmethod
    def load(self, source_path_or_name: str) -> GoldenDataset:
        """Load benchmark dataset from target source.

        Args:
            source_path_or_name (str): File path, URI, or dataset identifier.

        Returns:
            GoldenDataset: Loaded golden dataset container.
        """
        pass

    @abstractmethod
    def save(self, dataset: GoldenDataset, destination_path: str) -> bool:
        """Save golden dataset to target file path.

        Args:
            dataset (GoldenDataset): Dataset instance.
            destination_path (str): File export path.

        Returns:
            bool: True if successfully saved, False otherwise.
        """
        pass


class LocalBenchmarkLoader(BenchmarkLoader):
    """Loader for local filesystem datasets formatted in JSON or CSV."""

    def load_from_json(self, json_file_path: str) -> GoldenDataset:
        """Load golden dataset from a JSON file.

        Args:
            json_file_path (str): Absolute or relative JSON file path.

        Returns:
            GoldenDataset: Parsed golden dataset.
        """
        # Placeholder - file reading implemented in phase 2
        return GoldenDataset(
            dataset_id="local_json_dataset",
            name="Local JSON Benchmark",
            description="Loaded from local JSON file.",
        )

    def load_from_csv(self, csv_file_path: str) -> GoldenDataset:
        """Load golden dataset from a CSV file.

        Args:
            csv_file_path (str): CSV file path.

        Returns:
            GoldenDataset: Parsed golden dataset.
        """
        # Placeholder - CSV parsing implemented in phase 2
        return GoldenDataset(
            dataset_id="local_csv_dataset",
            name="Local CSV Benchmark",
            description="Loaded from local CSV file.",
        )

    def load(self, source_path_or_name: str) -> GoldenDataset:
        """Load benchmark dataset auto-detecting format.

        Args:
            source_path_or_name (str): Path to JSON or CSV dataset file.

        Returns:
            GoldenDataset: Loaded dataset instance.
        """
        if source_path_or_name.endswith(".csv"):
            return self.load_from_csv(source_path_or_name)
        return self.load_from_json(source_path_or_name)

    def save(self, dataset: GoldenDataset, destination_path: str) -> bool:
        """Save dataset to local JSON or CSV file.

        Args:
            dataset (GoldenDataset): Dataset instance.
            destination_path (str): Export path.

        Returns:
            bool: True if saved successfully.
        """
        # Placeholder save logic
        return True


class RemoteBenchmarkLoader(BenchmarkLoader):
    """Loader for remote datasets (e.g. HuggingFace benchmarks, SQuAD, HotpotQA)."""

    def load(self, source_path_or_name: str) -> GoldenDataset:
        """Load dataset from remote HuggingFace repository or API endpoint.

        Args:
            source_path_or_name (str): Dataset repository name or URL.

        Returns:
            GoldenDataset: Remote benchmark dataset.
        """
        # Placeholder remote fetch logic
        return GoldenDataset(
            dataset_id=source_path_or_name,
            name=f"Remote Benchmark: {source_path_or_name}",
            description="Loaded from remote benchmark repository.",
        )

    def save(self, dataset: GoldenDataset, destination_path: str) -> bool:
        """Save dataset to remote API endpoint.

        Args:
            dataset (GoldenDataset): Dataset instance.
            destination_path (str): Remote destination endpoint.

        Returns:
            bool: True if saved.
        """
        return True
