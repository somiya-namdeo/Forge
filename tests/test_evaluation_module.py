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
from app.metrics.custom_metrics import CustomEvaluator, TruLensEvaluator
from app.datasets.golden_dataset import GoldenDataset, GoldenSample
from app.thresholds.threshold_manager import (
    ThresholdManager,
    ThresholdRule,
    ThresholdOperator,
)
from app.utils.weighting import WeightingEngine, WeightPreset
from app.utils.score_calculator import ScoreCalculator
from app.history.evaluation_history import EvaluationHistoryManager, EvaluationRecord
from app.schemas.evaluation import (
    EvaluationRequest,
)
from app.services.evaluation_service import EvaluationService


class TestEvaluationModuleStructure(unittest.TestCase):
    """Test suite ensuring all evaluation module components function properly."""

    def setUp(self) -> None:
        self.service = EvaluationService()

    def test_metrics_registry_and_providers(self) -> None:
        registry = MetricRegistry()
        ragas = RagasEvaluator()
        trulens = TruLensEvaluator()
        custom = CustomEvaluator()

        registry.register_provider(ragas)
        registry.register_provider(trulens)
        registry.register_provider(custom)

        self.assertIn(EvaluationProvider.RAGAS, registry.list_providers())
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

    def test_service_run_evaluation(self) -> None:
        req = EvaluationRequest(
            question="What is the notice period?",
            answer="The notice period is 30 days.",
            contexts=["Termination notice period is 30 days."],
            ground_truth="30 days notice.",
        )
        resp = self.service.run_evaluation(req)
        self.assertIsNotNone(resp.evaluation_id)
        self.assertIsNotNone(resp.overall_score)


if __name__ == "__main__":
    unittest.main()
