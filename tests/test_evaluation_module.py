"""
Unit tests verifying the evaluation module architecture, schemas, services, and routes.
"""

import unittest
from app.metrics import (
    EvaluationProvider,
    MetricType,
    PassFailStatus,
    MetricRegistry,
)
from app.metrics.ragas_metrics import RagasEvaluator
from app.metrics.deepeval_metrics import DeepEvalEvaluator
from app.metrics.custom_metrics import CustomEvaluator, TruLensEvaluator
from app.datasets.golden_dataset import GoldenDataset, GoldenSample
from app.datasets.benchmark_loader import LocalBenchmarkLoader, RemoteBenchmarkLoader
from app.thresholds.threshold_manager import (
    ThresholdManager,
    ThresholdRule,
    ThresholdOperator,
)
from app.utils.weighting import WeightConfig, WeightingEngine, WeightPreset
from app.utils.score_calculator import ScoreCalculator
from app.history.evaluation_history import EvaluationHistoryManager, EvaluationRecord
from app.reports.report_generator import ReportGenerator
from app.reports.export_pdf import PDFExporter
from app.reports.export_json import JSONExporter
from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationSampleSchema,
    MetricConfigSchema,
    ThresholdConfigSchema,
    EvaluationHistoryFilter,
)
from app.services.evaluation_service import EvaluationService


class TestEvaluationModuleStructure(unittest.TestCase):
    """Test suite ensuring all evaluation module components function properly."""

    def setUp(self) -> None:
        self.service = EvaluationService()

    def test_metrics_registry_and_providers(self) -> None:
        registry = MetricRegistry()
        ragas = RagasEvaluator()
        deepeval = DeepEvalEvaluator()
        trulens = TruLensEvaluator()
        custom = CustomEvaluator()

        registry.register_provider(ragas)
        registry.register_provider(deepeval)
        registry.register_provider(trulens)
        registry.register_provider(custom)

        self.assertIn(EvaluationProvider.RAGAS, registry.list_providers())
        self.assertIn(EvaluationProvider.DEEPEVAL, registry.list_providers())
        self.assertIn(EvaluationProvider.TRULENS, registry.list_providers())
        self.assertIn(EvaluationProvider.CUSTOM, registry.list_providers())

    def test_golden_dataset_primitives(self) -> None:
        sample = GoldenSample(
            query="What is Forge?",
            expected_output="AI Engineering Decision Platform.",
            contexts=["Forge evaluates RAG architectures."],
        )
        dataset = GoldenDataset(
            dataset_id="test_ds",
            name="Test Dataset",
            samples=[sample],
        )
        self.assertEqual(len(dataset.samples), 1)
        self.assertTrue(dataset.validate())

    def test_threshold_manager(self) -> None:
        tm = ThresholdManager()
        tm.register_rule(
            ThresholdRule(
                metric_type=MetricType.FAITHFULNESS,
                target_score=0.8,
                operator=ThresholdOperator.GREATER_THAN_OR_EQUAL,
            )
        )
        res = tm.check_metric_threshold(MetricType.FAITHFULNESS, 0.85)
        self.assertEqual(res.status, PassFailStatus.PASS)

    def test_score_calculator(self) -> None:
        config = WeightingEngine.get_preset_config(WeightPreset.BALANCED_RAG)
        calc = ScoreCalculator(config)
        score = calc.calculate_composite_score({
            MetricType.FAITHFULNESS: 0.9,
            MetricType.ANSWER_RELEVANCE: 0.8,
        })
        self.assertGreater(score, 0.0)

    def test_history_manager(self) -> None:
        hm = EvaluationHistoryManager()
        rec = EvaluationRecord(
            rag_architecture_id="arch_1",
            dataset_id="ds_1",
            composite_score=0.85,
            overall_status=PassFailStatus.PASS,
        )
        saved = hm.save(rec)
        found = hm.get_by_id(saved.evaluation_id)
        self.assertIsNotNone(found)

    def test_report_generation_and_exports(self) -> None:
        rg = ReportGenerator()
        rep = rg.generate_report("eval_123", "pass", 0.85, {"faithfulness": 0.85})
        pdf_exp = PDFExporter()
        pdf_bytes = pdf_exp.export_to_pdf(rep)
        self.assertTrue(len(pdf_bytes) > 0)

        json_exp = JSONExporter()
        json_str = json_exp.export_to_json(rep)
        self.assertIn("eval_123", json_str)

    def test_service_run_evaluation(self) -> None:
        req = EvaluationRequest(
            evaluation_name="Test Run",
            rag_architecture_id="arch_test",
            samples=[
                EvaluationSampleSchema(
                    query="Test question",
                    actual_output="Test response",
                    contexts=["Test context"],
                )
            ],
        )
        resp = self.service.run_evaluation(req)
        self.assertIsNotNone(resp.evaluation_id)
        self.assertEqual(resp.overall_status, PassFailStatus.PASS)


if __name__ == "__main__":
    unittest.main()
