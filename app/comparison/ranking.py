"""
Ranking engine for Forge architecture comparison.

Computes multi-dimensional weighted composite scores, architecture strengths/weaknesses,
and rank explanations across benchmarked RAG architectures.
"""

from typing import Dict, List, Tuple

from app.comparison.comparison_models import (
    ArchitectureCandidate,
    OptimizationGoal,
    RankedArchitecture,
    RankingStrategy,
)


class RankingEngine:
    """Intelligent ranking engine for evaluating and ranking RAG architecture candidates."""

    @staticmethod
    def _extract_metrics(candidate: ArchitectureCandidate) -> Dict[str, float]:
        """Extract benchmark quality metrics, latency, and success rate from BenchmarkReport."""
        stats = candidate.benchmark_report.statistics

        average_score = getattr(stats, "average_score", 0.0)
        latency_ms = getattr(stats, "average_execution_time_ms", 0.0)

        # Success rate calculation
        total = getattr(stats, "total_samples", 0)
        passed = getattr(stats, "passed_samples", 0)
        if hasattr(stats, "success_rate"):
            success_rate = float(stats.success_rate)
        else:
            success_rate = (passed / total) if total > 0 else 1.0

        metric_averages = getattr(stats, "metric_averages", {}) or {}

        faithfulness = float(metric_averages.get("faithfulness", average_score))
        answer_relevancy = float(
            metric_averages.get("answer_relevancy", metric_averages.get("answer_relevance", average_score))
        )
        context_precision = float(metric_averages.get("context_precision", average_score))
        context_recall = float(metric_averages.get("context_recall", average_score))

        return {
            "overall_score": float(average_score),
            "faithfulness": faithfulness,
            "answer_relevancy": answer_relevancy,
            "context_precision": context_precision,
            "context_recall": context_recall,
            "average_latency_ms": float(latency_ms),
            "success_rate": float(success_rate),
        }

    @staticmethod
    def _compute_latency_score(latency_ms: float) -> float:
        """Normalize latency into range [0.0, 1.0] where faster latency yields higher score."""
        return max(0.0, min(1.0, 1.0 - (latency_ms / 5000.0)))

    def _calculate_score(
        self,
        candidate: ArchitectureCandidate,
        goal: OptimizationGoal,
        strategy: RankingStrategy = RankingStrategy.WEIGHTED_SCORE,
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate weighted comparison score based on strategy and optimization goal."""
        m = self._extract_metrics(candidate)
        latency_score = self._compute_latency_score(m["average_latency_ms"])

        # Determine effective ranking mode
        if strategy == RankingStrategy.HIGHEST_ACCURACY or goal == OptimizationGoal.QUALITY:
            score = (
                (m["overall_score"] * 0.30)
                + (m["faithfulness"] * 0.25)
                + (m["answer_relevancy"] * 0.20)
                + (m["context_precision"] * 0.15)
                + (m["context_recall"] * 0.10)
            )
        elif strategy == RankingStrategy.LOWEST_LATENCY or goal == OptimizationGoal.LATENCY:
            score = (
                (latency_score * 0.55)
                + (m["overall_score"] * 0.20)
                + (m["faithfulness"] * 0.15)
                + (m["success_rate"] * 0.10)
            )
        elif goal == OptimizationGoal.COST:
            score = (
                (latency_score * 0.40)
                + (m["overall_score"] * 0.30)
                + (m["success_rate"] * 0.30)
            )
        else:
            # Default BALANCED / WEIGHTED_SCORE strategy
            score = (
                (m["overall_score"] * 0.25)
                + (m["faithfulness"] * 0.20)
                + (m["answer_relevancy"] * 0.15)
                + (m["context_precision"] * 0.15)
                + (m["context_recall"] * 0.10)
                + (m["success_rate"] * 0.08)
                + (latency_score * 0.07)
            )

        return round(min(1.0, max(0.0, score)), 4), m

    @staticmethod
    def _compute_strengths_and_weaknesses(
        architecture_name: str,
        m: Dict[str, float],
    ) -> Tuple[List[str], List[str]]:
        """Generate architectural strengths and weaknesses based on metric benchmarks."""
        strengths: List[str] = []
        weaknesses: List[str] = []

        # Overall benchmark score
        if m["overall_score"] >= 0.85:
            strengths.append(f"High overall benchmark quality ({m['overall_score']:.2f})")
        elif m["overall_score"] < 0.70:
            weaknesses.append(f"Lower overall benchmark quality ({m['overall_score']:.2f})")

        # Faithfulness
        if m["faithfulness"] >= 0.85:
            strengths.append(f"High factual faithfulness ({m['faithfulness']:.2f})")
        elif m["faithfulness"] < 0.75:
            weaknesses.append(f"Poor factual faithfulness ({m['faithfulness']:.2f})")

        # Latency
        if m["average_latency_ms"] <= 500.0:
            strengths.append(f"Fast response retrieval latency ({m['average_latency_ms']:.0f} ms)")
        elif m["average_latency_ms"] > 3000.0:
            weaknesses.append(f"Higher response latency ({m['average_latency_ms']:.0f} ms)")

        # Success rate
        if m["success_rate"] >= 0.95:
            strengths.append(f"Excellent quality gate success rate ({m['success_rate']*100:.0f}%)")
        elif m["success_rate"] < 0.85:
            weaknesses.append(f"Lower quality gate pass rate ({m['success_rate']*100:.0f}%)")

        # Context recall & precision
        if m["context_recall"] >= 0.85:
            strengths.append(f"Strong context recall ({m['context_recall']:.2f})")
        elif m["context_recall"] < 0.75:
            weaknesses.append(f"Poor context recall ({m['context_recall']:.2f})")

        if m["context_precision"] >= 0.85:
            strengths.append(f"High context precision ({m['context_precision']:.2f})")
        elif m["context_precision"] < 0.75:
            weaknesses.append(f"Lower context signal-to-noise ratio ({m['context_precision']:.2f})")

        # Defaults if empty
        if not strengths:
            strengths.append("Standard retrieval performance")
        if not weaknesses:
            weaknesses.append("No critical weaknesses identified")

        return strengths, weaknesses

    @staticmethod
    def _generate_explanation(
        architecture_name: str,
        rank: int,
        overall_score: float,
        m: Dict[str, float],
    ) -> str:
        """Generate human-readable winner explanation."""
        if rank == 1:
            return (
                f"{architecture_name} ranked first because it achieved: "
                f"highest composite score ({overall_score:.4f}), "
                f"faithfulness ({m['faithfulness']:.2f}), "
                f"answer relevancy ({m['answer_relevancy']:.2f}), "
                f"and latency of {m['average_latency_ms']:.0f} ms with "
                f"{m['success_rate']*100:.0f}% success rate."
            )
        return (
            f"{architecture_name} ranked #{rank} with composite score of {overall_score:.4f} "
            f"and average latency of {m['average_latency_ms']:.0f} ms."
        )

    def rank(
        self,
        candidates: List[ArchitectureCandidate],
        goal: OptimizationGoal = OptimizationGoal.BALANCED,
        strategy: RankingStrategy = RankingStrategy.WEIGHTED_SCORE,
    ) -> List[RankedArchitecture]:
        """Rank architecture candidates according to optimization goal and strategy."""
        scored_candidates = []

        for candidate in candidates:
            overall_score, m = self._calculate_score(candidate, goal, strategy)
            strengths, weaknesses = self._compute_strengths_and_weaknesses(candidate.architecture_name, m)
            scored_candidates.append((overall_score, candidate, m, strengths, weaknesses))

        # Sort candidates descending by overall composite score
        scored_candidates.sort(key=lambda item: item[0], reverse=True)

        ranked: List[RankedArchitecture] = []
        for idx, (overall_score, candidate, m, strengths, weaknesses) in enumerate(scored_candidates, start=1):
            explanation = self._generate_explanation(candidate.architecture_name, idx, overall_score, m)

            ranked.append(
                RankedArchitecture(
                    rank=idx,
                    architecture_id=candidate.architecture_id,
                    architecture_name=candidate.architecture_name,
                    overall_score=overall_score,
                    benchmark_score=m["overall_score"],
                    average_latency_ms=m["average_latency_ms"],
                    faithfulness=m["faithfulness"],
                    answer_relevancy=m["answer_relevancy"],
                    context_precision=m["context_precision"],
                    context_recall=m["context_recall"],
                    success_rate=m["success_rate"],
                    strengths=strengths,
                    weaknesses=weaknesses,
                    explanation=explanation,
                    reason=f"Ranked using '{strategy.value}' strategy with '{goal.value}' goal.",
                )
            )

        return ranked