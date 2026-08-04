"""Dataset loader module for Forge benchmark evaluation samples."""

import json
from pathlib import Path

from pydantic import ValidationError

from app.benchmark.benchmark_models import BenchmarkSample

_DEFAULT_DATASET_PATH = Path(__file__).resolve().parent / "forge_benchmark.json"


class BenchmarkLoader:
    """Loader responsible for reading and validating benchmark dataset files."""

    @staticmethod
    def load(path: str | Path) -> list[BenchmarkSample]:
        """Load and validate benchmark samples from a JSON dataset file."""
        file_path = Path(path).resolve()

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(
                f"Benchmark dataset file not found or is not a file: '{file_path}'"
            )

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Malformed JSON in benchmark file '{file_path}': {exc}") from exc
        except OSError as exc:
            raise ValueError(f"Failed to read benchmark file '{file_path}': {exc}") from exc

        if not isinstance(data, list):
            raise ValueError(
                f"Invalid dataset structure in '{file_path}'. Expected a JSON array of samples."
            )

        samples: list[BenchmarkSample] = []
        for idx, entry in enumerate(data):
            try:
                sample = BenchmarkSample.model_validate(entry)
                samples.append(sample)
            except ValidationError as exc:
                raise ValueError(
                    f"Validation failed for benchmark sample at index {idx} in '{file_path}': {exc}"
                ) from exc

        return samples

    @classmethod
    def load_default(cls) -> list[BenchmarkSample]:
        """Load default Forge benchmark dataset from disk."""
        return cls.load(_DEFAULT_DATASET_PATH)


LocalBenchmarkLoader = BenchmarkLoader
BenchmarkDatasetLoader = BenchmarkLoader
RemoteBenchmarkLoader = BenchmarkLoader
