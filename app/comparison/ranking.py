"""
Ranking engine for Forge architecture comparison (v2.0).

Consumes BenchmarkReport v2.0 to rank architectures across multiple quality
dimensions. Does NOT call EvaluationEngine or BenchmarkEngine — consumes
pre-computed BenchmarkReport data only.
"""

from typing import Dict, List, Tuple

from app.comparison.comparison_models import (
    ArchitectureCandidate,
    ArchitectureMetadata,
    OptimizationGoal,
    RankedArchitecture,
    RankingStrategy,
)

# ─── Grade → numeric value (for tie-breaking and sorting) ────────────────────
_GRADE_ORDER = {"A+": 6, "A": 5, "B": 4, "C": 3, "D": 2, "F": 1, "": 0}


class RankingEngine:
    """Intelligent ranking engine for evaluating and ranking RAG architecture candidates.

    Consumes BenchmarkReport v2.0 fields. Does NOT call EvaluationEngine or
    BenchmarkEngine. All metric data is consumed from pre-computed reports.
    """

    # ─── Extraction ───────────────────────────────────────────────────────────

    @staticmethod
    def _extract_metrics(candidate: ArchitectureCandidate) -> Dict:
        """Extract full metric set from BenchmarkReport v2.0.

        Returns a unified dict with all relevant data for ranking and analysis.
        Consumes BenchmarkReport only — no Evaluation or Benchmark logic.
        """
        report = candidate.benchmark_report
        stats = report.statistics

        # ── Core scores ──────────────────────────────────────────────────────
        average_score = float(getattr(stats, "average_score", 0.0))
        latency_ms = float(getattr(stats, "average_execution_time_ms", 0.0))
        success_rate = float(getattr(stats, "success_rate", 1.0))
        total_samples = int(getattr(stats, "total_samples", 0))
        passed_samples = int(getattr(stats, "passed_samples", 0))
        if total_samples > 0 and not hasattr(stats, "success_rate"):
            success_rate = passed_samples / total_samples

        # ── Full flat metric averages (17 metrics) ───────────────────────────
        metric_averages: Dict[str, float] = dict(getattr(stats, "metric_averages", {}) or {})

        # ── Per-category averages (v2.0 fields) ──────────────────────────────
        gen_avgs: Dict[str, float] = dict(getattr(stats, "generation_metric_averages", {}) or {})
        ret_avgs: Dict[str, float] = dict(getattr(stats, "retrieval_metric_averages", {}) or {})
        ops_avgs: Dict[str, float] = dict(getattr(stats, "operational_metric_averages", {}) or {})

        # ── Diagnostic fields (v2.0) ─────────────────────────────────────────
        quality_grade: str = getattr(report, "quality_grade", "") or ""
        deployment_readiness: str = getattr(report, "deployment_readiness", "") or ""
        grade_distribution: Dict[str, int] = dict(getattr(stats, "grade_distribution", {}) or {})
        top_strengths: List[str] = list(getattr(stats, "top_strengths", []) or [])
        top_weaknesses: List[str] = list(getattr(stats, "top_weaknesses", []) or [])
        top_recommendations: List[str] = list(getattr(stats, "top_recommendations", []) or [])
        fallback_rate: float = float(getattr(report, "fallback_rate", 0.0))
        provider_summary: Dict = dict(getattr(report, "provider_summary", {}) or {})

        # ── Executive summary (v2.0) ──────────────────────────────────────────
        exec_summary = getattr(report, "executive_summary", None)
        executive_verdict: str = getattr(exec_summary, "overall_verdict", "") if exec_summary else ""

        # ── Convenience aliases for scoring formulas ──────────────────────────
        def _m(key: str) -> float:
            return float(metric_averages.get(key, gen_avgs.get(key, ret_avgs.get(key, ops_avgs.get(key, average_score)))))

        return {
            # Core
            "overall_score": average_score,
            "average_latency_ms": latency_ms,
            "success_rate": success_rate,
            # Generation
            "faithfulness": _m("faithfulness"),
            "answer_relevancy": _m("answer_relevancy"),
            "context_precision": _m("context_precision"),
            "context_recall": _m("context_recall"),
            "groundedness": _m("groundedness"),
            "hallucination_score": _m("hallucination_score"),
            "completeness": _m("completeness"),
            "coherence": _m("coherence"),
            # Retrieval
            "precision_at_k": _m("precision_at_k"),
            "recall_at_k": _m("recall_at_k"),
            "hit_rate": _m("hit_rate"),
            "mrr": _m("mrr"),
            "ndcg": _m("ndcg"),
            # Operational
            "latency_ms": _m("latency_ms"),
            "token_usage": _m("token_usage"),
            "estimated_cost_usd": _m("estimated_cost_usd"),
            "throughput": _m("throughput_tokens_per_second"),
            # v2.0 diagnostic
            "quality_grade": quality_grade,
            "deployment_readiness": deployment_readiness,
            "grade_distribution": grade_distribution,
            "top_strengths": top_strengths,
            "top_weaknesses": top_weaknesses,
            "top_recommendations": top_recommendations,
            "fallback_rate": fallback_rate,
            "provider_summary": provider_summary,
            "executive_verdict": executive_verdict,
            # Full metric map
            "metric_averages": metric_averages,
        }

    @staticmethod
    def _compute_latency_score(latency_ms: float) -> float:
        """Normalize latency to [0.0, 1.0] — faster is higher."""
        return max(0.0, min(1.0, 1.0 - (latency_ms / 5000.0)))

    @staticmethod
    def _compute_cost_score(estimated_cost: float) -> float:
        """Normalize cost — lower cost is higher score."""
        return max(0.0, min(1.0, estimated_cost))

    # ─── Scoring ──────────────────────────────────────────────────────────────

    def _calculate_score(
        self,
        candidate: ArchitectureCandidate,
        goal: OptimizationGoal,
        strategy: RankingStrategy = RankingStrategy.WEIGHTED_SCORE,
    ) -> Tuple[float, Dict]:
        """Calculate weighted composite comparison score.

        Uses full v2.0 metric set from BenchmarkReport. Does not re-run evaluation.
        """
        m = self._extract_metrics(candidate)
        latency_score = self._compute_latency_score(m["average_latency_ms"])
        cost_score = self._compute_cost_score(m["estimated_cost_usd"])

        if strategy == RankingStrategy.HIGHEST_ACCURACY or goal == OptimizationGoal.QUALITY:
            score = (
                m["overall_score"] * 0.20
                + m["faithfulness"] * 0.18
                + m["groundedness"] * 0.12
                + m["answer_relevancy"] * 0.12
                + m["hallucination_score"] * 0.10
                + m["context_recall"] * 0.10
                + m["context_precision"] * 0.08
                + m["mrr"] * 0.05
                + m["completeness"] * 0.05
            )
        elif strategy == RankingStrategy.LOWEST_LATENCY or goal == OptimizationGoal.LATENCY:
            score = (
                latency_score * 0.50
                + m["overall_score"] * 0.20
                + m["faithfulness"] * 0.15
                + m["success_rate"] * 0.10
                + m["throughput"] * 0.05
            )
        elif goal == OptimizationGoal.COST:
            score = (
                cost_score * 0.35
                + latency_score * 0.25
                + m["overall_score"] * 0.25
                + m["success_rate"] * 0.15
            )
        else:
            # Default BALANCED / WEIGHTED_SCORE
            score = (
                m["overall_score"] * 0.20
                + m["faithfulness"] * 0.15
                + m["groundedness"] * 0.10
                + m["answer_relevancy"] * 0.10
                + m["hallucination_score"] * 0.08
                + m["context_precision"] * 0.08
                + m["context_recall"] * 0.08
                + m["mrr"] * 0.05
                + m["success_rate"] * 0.07
                + latency_score * 0.05
                + m["completeness"] * 0.04
            )

        return round(min(1.0, max(0.0, score)), 4), m

    # ─── Strengths / Weaknesses / Recommendations ─────────────────────────────

    @staticmethod
    def _compute_strengths_and_weaknesses(
        architecture_name: str,
        m: Dict,
    ) -> Tuple[List[str], List[str]]:
        """Generate strengths and weaknesses from full v2.0 metric set.

        Falls back to pre-computed BenchmarkReport top_strengths/top_weaknesses
        when available for richer diagnostic output.
        """
        strengths: List[str] = []
        weaknesses: List[str] = []

        # Overall score
        if m["overall_score"] >= 0.85:
            strengths.append(f"High overall benchmark quality ({m['overall_score']:.2f})")
        elif m["overall_score"] < 0.70:
            weaknesses.append(f"Lower overall benchmark quality ({m['overall_score']:.2f})")

        # Faithfulness
        if m["faithfulness"] >= 0.85:
            strengths.append(f"High factual faithfulness ({m['faithfulness']:.2f})")
        elif m["faithfulness"] < 0.75:
            weaknesses.append(f"Poor factual faithfulness ({m['faithfulness']:.2f})")

        # Groundedness
        if m["groundedness"] >= 0.85:
            strengths.append(f"Excellent groundedness ({m['groundedness']:.2f})")
        elif m["groundedness"] < 0.70:
            weaknesses.append(f"Low groundedness — answers may be unanchored ({m['groundedness']:.2f})")

        # Hallucination
        if m["hallucination_score"] >= 0.90:
            strengths.append(f"Near-zero hallucination rate ({m['hallucination_score']:.2f})")
        elif m["hallucination_score"] < 0.70:
            weaknesses.append(f"High hallucination risk ({m['hallucination_score']:.2f})")

        # Latency
        if m["average_latency_ms"] <= 300.0:
            strengths.append(f"Fast response latency ({m['average_latency_ms']:.0f} ms)")
        elif m["average_latency_ms"] > 2000.0:
            weaknesses.append(f"High response latency ({m['average_latency_ms']:.0f} ms)")

        # Success rate
        if m["success_rate"] >= 0.95:
            strengths.append(f"Excellent quality gate pass rate ({m['success_rate']*100:.0f}%)")
        elif m["success_rate"] < 0.85:
            weaknesses.append(f"Lower quality gate pass rate ({m['success_rate']*100:.0f}%)")

        # Retrieval
        if m["context_recall"] >= 0.85:
            strengths.append(f"Strong context recall ({m['context_recall']:.2f})")
        elif m["context_recall"] < 0.70:
            weaknesses.append(f"Poor context recall ({m['context_recall']:.2f})")

        if m["context_precision"] >= 0.85:
            strengths.append(f"High context precision ({m['context_precision']:.2f})")
        elif m["context_precision"] < 0.70:
            weaknesses.append(f"Noisy context retrieval ({m['context_precision']:.2f})")

        if m["mrr"] >= 0.80:
            strengths.append(f"Strong MRR ranking quality ({m['mrr']:.2f})")
        elif m["mrr"] < 0.50:
            weaknesses.append(f"Weak MRR — relevant results not ranked first ({m['mrr']:.2f})")

        # Coherence
        if m["coherence"] < 0.60:
            weaknesses.append(f"Generated responses lack coherence ({m['coherence']:.2f})")
        elif m["coherence"] >= 0.80:
            strengths.append(f"Well-structured coherent responses ({m['coherence']:.2f})")

        # Completeness
        if m["completeness"] < 0.65:
            weaknesses.append(f"Answers appear incomplete ({m['completeness']:.2f})")

        # Enrich with pre-computed BenchmarkReport diagnostics
        bm_strengths: List[str] = m.get("top_strengths", [])
        bm_weaknesses: List[str] = m.get("top_weaknesses", [])
        for s in bm_strengths[:2]:
            if s not in strengths:
                strengths.append(s)
        for w in bm_weaknesses[:2]:
            if w not in weaknesses:
                weaknesses.append(w)

        if not strengths:
            strengths.append("Standard retrieval performance")
        if not weaknesses:
            weaknesses.append("No critical weaknesses identified")

        return strengths, weaknesses

    @staticmethod
    def _generate_explanation(architecture_name: str, rank: int, overall_score: float, m: Dict) -> str:
        """Generate human-readable rank explanation."""
        grade = m.get("quality_grade", "")
        readiness = m.get("deployment_readiness", "")
        if rank == 1:
            return (
                f"{architecture_name} ranked #1 — composite score {overall_score:.4f} "
                f"(grade: {grade}, readiness: {readiness}), "
                f"faithfulness {m['faithfulness']:.2f}, groundedness {m['groundedness']:.2f}, "
                f"hallucination {m['hallucination_score']:.2f}, latency {m['average_latency_ms']:.0f} ms."
            )
        return (
            f"{architecture_name} ranked #{rank} — composite score {overall_score:.4f} "
            f"(grade: {grade}, readiness: {readiness}), "
            f"latency {m['average_latency_ms']:.0f} ms."
        )

    # ─── Main ranking ──────────────────────────────────────────────────────────

    def rank(
        self,
        candidates: List[ArchitectureCandidate],
        goal: OptimizationGoal = OptimizationGoal.BALANCED,
        strategy: RankingStrategy = RankingStrategy.WEIGHTED_SCORE,
    ) -> List[RankedArchitecture]:
        """Rank architecture candidates. Consumes BenchmarkReport only.

        Returns a sorted list of RankedArchitecture with full v2.0 fields.
        """
        scored: List[Tuple[float, ArchitectureCandidate, Dict, List[str], List[str]]] = []

        for candidate in candidates:
            overall_score, m = self._calculate_score(candidate, goal, strategy)
            strengths, weaknesses = self._compute_strengths_and_weaknesses(
                candidate.architecture_name, m
            )
            scored.append((overall_score, candidate, m, strengths, weaknesses))

        scored.sort(key=lambda item: (item[0], _GRADE_ORDER.get(item[2].get("quality_grade", ""), 0)), reverse=True)

        ranked: List[RankedArchitecture] = []
        for idx, (overall_score, candidate, m, strengths, weaknesses) in enumerate(scored, start=1):
            explanation = self._generate_explanation(candidate.architecture_name, idx, overall_score, m)
            arch_meta = candidate.architecture_metadata if hasattr(candidate, "architecture_metadata") else ArchitectureMetadata()

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
                    # v2.0 fields
                    quality_grade=m.get("quality_grade", ""),
                    deployment_readiness=m.get("deployment_readiness", ""),
                    grade_distribution=m.get("grade_distribution", {}),
                    metric_averages=m.get("metric_averages", {}),
                    recommendations=m.get("top_recommendations", [])[:3],
                    architecture_metadata=arch_meta,
                    fallback_rate=m.get("fallback_rate", 0.0),
                )
            )

        return ranked