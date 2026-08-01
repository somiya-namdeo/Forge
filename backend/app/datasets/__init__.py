"""
Evaluation Datasets Package.

Provides data primitives for golden evaluation datasets, ground-truth samples,
and benchmark loaders for standard datasets (SQuAD, HotpotQA, MS MARCO, custom).
"""

from backend.app.datasets.benchmark_loader import BenchmarkLoader, LocalBenchmarkLoader
from backend.app.datasets.golden_dataset import GoldenDataset, GoldenSample

__all__ = [
    "GoldenSample",
    "GoldenDataset",
    "BenchmarkLoader",
    "LocalBenchmarkLoader",
]
