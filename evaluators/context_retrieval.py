"""
Context Retrieval Evaluation for RAG systems.
Uses DeepEval's ContextualRelevancyMetric and ContextualRecallMetric.
"""

from typing import Optional
from deepeval.metrics import ContextualRelevancyMetric, ContextualRecallMetric, ContextualPrecisionMetric
from config import EvaluationConfig


def create_contextual_relevancy_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> ContextualRelevancyMetric:
    """
    Create ContextualRelevancyMetric to evaluate if retrieved context is relevant.

    This metric evaluates whether the context retrieved by RAG contains
    information relevant to answering the user's question.

    Args:
        threshold: Minimum score for passing (0-1)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured ContextualRelevancyMetric
    """
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    model_config = EvaluationConfig.get_model_config()

    return ContextualRelevancyMetric(
        threshold=threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


def create_contextual_recall_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> ContextualRecallMetric:
    """
    Create ContextualRecallMetric to evaluate retrieval completeness.

    This metric measures whether all necessary information from the
    expected context was retrieved by the RAG system.

    Args:
        threshold: Minimum score for passing (0-1)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured ContextualRecallMetric
    """
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    model_config = EvaluationConfig.get_model_config()

    return ContextualRecallMetric(
        threshold=threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


def create_contextual_precision_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> ContextualPrecisionMetric:
    """
    Create ContextualPrecisionMetric to evaluate retrieval precision.

    This metric measures how much of the retrieved context is actually
    relevant vs. noise/irrelevant information.

    Args:
        threshold: Minimum score for passing (0-1)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured ContextualPrecisionMetric
    """
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    model_config = EvaluationConfig.get_model_config()

    return ContextualPrecisionMetric(
        threshold=threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


class ContextRetrievalEvaluator:
    """
    Comprehensive evaluator for RAG context retrieval quality.

    Combines multiple metrics to evaluate:
    - Relevancy: Is the retrieved context relevant to the question?
    - Recall: Did we retrieve all necessary information?
    - Precision: How much retrieved context is actually useful?
    """

    def __init__(
        self,
        threshold: Optional[float] = None,
        include_reason: bool = True,
    ):
        """
        Initialize the context retrieval evaluator with multiple metrics.

        Args:
            threshold: Minimum score for passing
            include_reason: Include reasoning in metric outputs
        """
        self.threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
        self.include_reason = include_reason or EvaluationConfig.DEEPEVAL_VERBOSE

        # Initialize all context metrics
        self.relevancy_metric = create_contextual_relevancy_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

        self.recall_metric = create_contextual_recall_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

        self.precision_metric = create_contextual_precision_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

    def get_all_metrics(self):
        """Get list of all context retrieval metrics."""
        return [
            self.relevancy_metric,
            self.recall_metric,
            self.precision_metric,
        ]

    def evaluate_context_quality(
        self,
        question: str,
        retrieved_contexts: list[str],
        expected_contexts: list[str],
    ) -> dict:
        """
        Evaluate context retrieval quality across all dimensions.

        Args:
            question: The user's question/input
            retrieved_contexts: List of context chunks retrieved by RAG
            expected_contexts: List of expected/golden context chunks

        Returns:
            Dict with scores for each metric
        """
        from deepeval.test_case import LLMTestCase

        # Create test case
        test_case = LLMTestCase(
            input=question,
            actual_output="",  # Not needed for context metrics
            retrieval_context=retrieved_contexts,
            expected_output="",  # Not needed for context metrics
            context=expected_contexts,  # Golden/expected contexts
        )

        results = {}

        # Evaluate relevancy
        try:
            self.relevancy_metric.measure(test_case)
            results["contextual_relevancy"] = {
                "score": self.relevancy_metric.score,
                "passed": self.relevancy_metric.score >= self.threshold,
                "reason": getattr(self.relevancy_metric, "reason", None),
            }
        except Exception as e:
            results["contextual_relevancy"] = {"error": str(e)}

        # Evaluate recall
        try:
            self.recall_metric.measure(test_case)
            results["contextual_recall"] = {
                "score": self.recall_metric.score,
                "passed": self.recall_metric.score >= self.threshold,
                "reason": getattr(self.recall_metric, "reason", None),
            }
        except Exception as e:
            results["contextual_recall"] = {"error": str(e)}

        # Evaluate precision
        try:
            self.precision_metric.measure(test_case)
            results["contextual_precision"] = {
                "score": self.precision_metric.score,
                "passed": self.precision_metric.score >= self.threshold,
                "reason": getattr(self.precision_metric, "reason", None),
            }
        except Exception as e:
            results["contextual_precision"] = {"error": str(e)}

        # Calculate aggregate score (average of all metrics)
        valid_scores = [
            r["score"] for r in results.values()
            if "score" in r
        ]
        if valid_scores:
            results["aggregate_score"] = sum(valid_scores) / len(valid_scores)
            results["all_passed"] = all(
                r.get("passed", False) for r in results.values()
                if "passed" in r
            )
        else:
            results["aggregate_score"] = 0.0
            results["all_passed"] = False

        return results
