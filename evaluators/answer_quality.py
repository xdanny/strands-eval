"""
Answer Quality Evaluation for SQL Agent outputs.
Uses DeepEval's AnswerRelevancyMetric and FaithfulnessMetric.
"""

from typing import Optional
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, HallucinationMetric
from config import EvaluationConfig


def create_answer_relevancy_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> AnswerRelevancyMetric:
    """
    Create AnswerRelevancyMetric to evaluate answer relevance to question.

    This metric evaluates whether the generated answer is relevant to
    the user's question, regardless of factual accuracy.

    Args:
        threshold: Minimum score for passing (0-1)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured AnswerRelevancyMetric
    """
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    model_config = EvaluationConfig.get_model_config()

    return AnswerRelevancyMetric(
        threshold=threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


def create_faithfulness_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> FaithfulnessMetric:
    """
    Create FaithfulnessMetric to evaluate factual accuracy.

    This metric evaluates whether the answer is factually grounded
    in the provided context (no hallucinations).

    Args:
        threshold: Minimum score for passing (0-1)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured FaithfulnessMetric
    """
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    model_config = EvaluationConfig.get_model_config()

    return FaithfulnessMetric(
        threshold=threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


def create_hallucination_metric(
    threshold: Optional[float] = None,
    include_reason: bool = True,
) -> HallucinationMetric:
    """
    Create HallucinationMetric to detect hallucinated information.

    This metric detects when the answer contains information not
    present in the context.

    Args:
        threshold: Maximum acceptable hallucination score (lower is better)
        include_reason: Whether to include reasoning in output

    Returns:
        Configured HallucinationMetric
    """
    # For hallucination, lower is better, so we use 1 - threshold
    # If threshold is 0.7, we want hallucination <= 0.3
    threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
    hallucination_threshold = 1.0 - threshold

    model_config = EvaluationConfig.get_model_config()

    return HallucinationMetric(
        threshold=hallucination_threshold,
        model=model_config.get("model"),
        include_reason=include_reason,
    )


class AnswerQualityEvaluator:
    """
    Comprehensive evaluator for answer quality.

    Combines multiple metrics to evaluate:
    - Relevancy: Is the answer relevant to the question?
    - Faithfulness: Is the answer factually grounded in context?
    - Hallucination: Does the answer contain fabricated information?
    """

    def __init__(
        self,
        threshold: Optional[float] = None,
        include_reason: bool = True,
    ):
        """
        Initialize the answer quality evaluator with multiple metrics.

        Args:
            threshold: Minimum score for passing
            include_reason: Include reasoning in metric outputs
        """
        self.threshold = threshold or EvaluationConfig.DEEPEVAL_THRESHOLD
        self.include_reason = include_reason or EvaluationConfig.DEEPEVAL_VERBOSE

        # Initialize all answer quality metrics
        self.relevancy_metric = create_answer_relevancy_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

        self.faithfulness_metric = create_faithfulness_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

        self.hallucination_metric = create_hallucination_metric(
            threshold=self.threshold,
            include_reason=self.include_reason,
        )

    def get_all_metrics(self):
        """Get list of all answer quality metrics."""
        return [
            self.relevancy_metric,
            self.faithfulness_metric,
            self.hallucination_metric,
        ]

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        retrieved_contexts: list[str],
        expected_answer: Optional[str] = None,
    ) -> dict:
        """
        Evaluate answer quality across all dimensions.

        Args:
            question: The user's question/input
            answer: The generated answer
            retrieved_contexts: List of context chunks used to generate answer
            expected_answer: Optional expected/golden answer for comparison

        Returns:
            Dict with scores for each metric
        """
        from deepeval.test_case import LLMTestCase

        # Create test case
        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=retrieved_contexts,
            expected_output=expected_answer or "",
        )

        results = {}

        # Evaluate relevancy
        try:
            self.relevancy_metric.measure(test_case)
            results["answer_relevancy"] = {
                "score": self.relevancy_metric.score,
                "passed": self.relevancy_metric.score >= self.threshold,
                "reason": getattr(self.relevancy_metric, "reason", None),
            }
        except Exception as e:
            results["answer_relevancy"] = {"error": str(e)}

        # Evaluate faithfulness
        try:
            self.faithfulness_metric.measure(test_case)
            results["faithfulness"] = {
                "score": self.faithfulness_metric.score,
                "passed": self.faithfulness_metric.score >= self.threshold,
                "reason": getattr(self.faithfulness_metric, "reason", None),
            }
        except Exception as e:
            results["faithfulness"] = {"error": str(e)}

        # Evaluate hallucination (note: lower is better)
        try:
            self.hallucination_metric.measure(test_case)
            hallucination_threshold = 1.0 - self.threshold
            results["hallucination"] = {
                "score": self.hallucination_metric.score,
                "passed": self.hallucination_metric.score <= hallucination_threshold,
                "reason": getattr(self.hallucination_metric, "reason", None),
                "note": "Lower score is better for hallucination",
            }
        except Exception as e:
            results["hallucination"] = {"error": str(e)}

        # Calculate aggregate score
        # For relevancy and faithfulness, higher is better
        # For hallucination, lower is better (so we invert it)
        scores = []
        if "score" in results.get("answer_relevancy", {}):
            scores.append(results["answer_relevancy"]["score"])
        if "score" in results.get("faithfulness", {}):
            scores.append(results["faithfulness"]["score"])
        if "score" in results.get("hallucination", {}):
            # Invert hallucination score (1 - score) so higher is better
            scores.append(1.0 - results["hallucination"]["score"])

        if scores:
            results["aggregate_score"] = sum(scores) / len(scores)
            results["all_passed"] = all(
                r.get("passed", False) for r in [
                    results.get("answer_relevancy", {}),
                    results.get("faithfulness", {}),
                    results.get("hallucination", {}),
                ]
                if "passed" in r
            )
        else:
            results["aggregate_score"] = 0.0
            results["all_passed"] = False

        return results


def evaluate_sql_answer_quality(
    question: str,
    generated_sql: str,
    final_answer: str,
    retrieved_contexts: list[str],
    expected_answer_keywords: Optional[list[str]] = None,
) -> dict:
    """
    Specialized evaluation for SQL agent answers.

    Args:
        question: User's business question
        generated_sql: The SQL query generated
        final_answer: Natural language answer provided to user
        retrieved_contexts: Context retrieved from schema/docs
        expected_answer_keywords: Keywords that should appear in answer

    Returns:
        Dict with evaluation results
    """
    evaluator = AnswerQualityEvaluator()

    # Evaluate the final answer
    results = evaluator.evaluate_answer(
        question=question,
        answer=final_answer,
        retrieved_contexts=retrieved_contexts,
    )

    # Add SQL-specific checks
    results["sql_included"] = generated_sql.strip() in final_answer or "sql" in final_answer.lower()

    # Check for expected keywords
    if expected_answer_keywords:
        found_keywords = [
            kw for kw in expected_answer_keywords
            if kw.lower() in final_answer.lower()
        ]
        results["keyword_coverage"] = {
            "found": found_keywords,
            "missing": [kw for kw in expected_answer_keywords if kw not in found_keywords],
            "coverage_ratio": len(found_keywords) / len(expected_answer_keywords),
        }

    return results
