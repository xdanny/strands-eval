"""
Main evaluation test suite for SQL agent.

This uses pytest and DeepEval to evaluate the SQL agent across
all test cases with multiple metrics.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any, List

from deepeval import assert_test
from deepeval.test_case import LLMTestCase

# Import evaluators
from evaluators.sql_correctness import create_sql_correctness_metric, SqlCorrectnessMetric
from evaluators.context_retrieval import ContextRetrievalEvaluator
from evaluators.answer_quality import AnswerQualityEvaluator
from evaluators.query_efficiency import evaluate_query_efficiency

# Import agent runner
from agent.sql_agent_runner import create_sql_agent_runner

from config import EvaluationConfig

# Validate configuration at module load time
EvaluationConfig.validate_config()


# Load test data
def load_test_cases() -> List[Dict[str, Any]]:
    """Load test cases from JSON file."""
    test_cases_path = Path("datasets/test_cases.json")
    with open(test_cases_path, "r") as f:
        data = json.load(f)
    return data["test_cases"]


def load_golden_contexts() -> Dict[str, Any]:
    """Load golden contexts from JSON file."""
    contexts_path = Path("datasets/golden_contexts.json")
    with open(contexts_path, "r") as f:
        return json.load(f)


# Load data once for all tests
TEST_CASES = load_test_cases()
GOLDEN_CONTEXTS = load_golden_contexts()


# Create agent runner
@pytest.fixture(scope="module")
def agent_runner():
    """Create SQL agent runner instance."""
    return create_sql_agent_runner(
        schema_path="datasets/analytics_schema.json",
        agent_config={
            "model": EvaluationConfig.EVAL_MODEL,
        },
    )


# Parameterize tests with all test cases
@pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc["id"] for tc in TEST_CASES])
@pytest.mark.sql_agent
def test_sql_agent_complete_evaluation(test_case: Dict[str, Any], agent_runner):
    """
    Complete evaluation of SQL agent for a single test case.

    Tests all aspects:
    - SQL correctness
    - Context retrieval quality
    - Answer quality
    - Query efficiency
    """
    # Extract test case data
    test_id = test_case["id"]
    question = test_case["question"]
    expected_sql = test_case["expected_sql"]
    expected_context = GOLDEN_CONTEXTS["contexts"].get(test_id, {}).get("required_context", [])
    sql_criteria = test_case.get("sql_criteria", {})

    print(f"\n{'=' * 80}")
    print(f"Test Case: {test_id}")
    print(f"Question: {question}")
    print(f"Difficulty: {test_case.get('difficulty', 'unknown')}")
    print(f"{'=' * 80}\n")

    # Run the agent
    result = agent_runner.run(question)

    # Check for errors
    if result.error:
        pytest.fail(f"Agent execution failed: {result.error}")

    print(f"Generated SQL:\n{result.generated_sql}\n")
    print(f"Final Answer:\n{result.final_answer}\n")
    print(f"Execution Time: {result.execution_time_ms:.2f}ms\n")

    # Initialize evaluators
    sql_metric = create_sql_correctness_metric()
    context_evaluator = ContextRetrievalEvaluator()
    answer_evaluator = AnswerQualityEvaluator()

    # Create DeepEval test case
    deepeval_test_case = LLMTestCase(
        input=question,
        actual_output=result.generated_sql,
        expected_output=expected_sql,
        retrieval_context=result.retrieved_contexts,
        context=expected_context,
    )

    # Evaluate SQL Correctness
    print("Evaluating SQL Correctness...")
    try:
        assert_test(deepeval_test_case, [sql_metric])
        print(f"✓ SQL Correctness Score: {sql_metric.score:.2f}")
    except AssertionError as e:
        print(f"✗ SQL Correctness Failed: {e}")
        # Continue with other evaluations

    # Validate against criteria
    if sql_criteria:
        print("\nValidating against SQL criteria...")
        validation = sql_metric.validate_against_criteria(
            actual_sql=result.generated_sql,
            expected_sql=expected_sql,
            criteria=sql_criteria,
        )

        if not validation["passed"]:
            print(f"✗ Criteria validation failed:")
            for failure in validation["failures"]:
                print(f"  - {failure}")

        for warning in validation["warnings"]:
            print(f"  ⚠ {warning}")

    # Evaluate Context Retrieval
    print("\nEvaluating Context Retrieval...")
    context_results = context_evaluator.evaluate_context_quality(
        question=question,
        retrieved_contexts=result.retrieved_contexts,
        expected_contexts=expected_context,
    )

    print(f"  Contextual Relevancy: {context_results.get('contextual_relevancy', {}).get('score', 0):.2f}")
    print(f"  Contextual Recall: {context_results.get('contextual_recall', {}).get('score', 0):.2f}")
    print(f"  Contextual Precision: {context_results.get('contextual_precision', {}).get('score', 0):.2f}")
    print(f"  Aggregate Score: {context_results.get('aggregate_score', 0):.2f}")

    # Evaluate Answer Quality
    print("\nEvaluating Answer Quality...")
    answer_results = answer_evaluator.evaluate_answer(
        question=question,
        answer=result.final_answer,
        retrieved_contexts=result.retrieved_contexts,
        expected_answer=None,  # We don't have expected answers in this format
    )

    print(f"  Answer Relevancy: {answer_results.get('answer_relevancy', {}).get('score', 0):.2f}")
    print(f"  Faithfulness: {answer_results.get('faithfulness', {}).get('score', 0):.2f}")
    print(f"  Hallucination: {answer_results.get('hallucination', {}).get('score', 0):.2f}")
    print(f"  Aggregate Score: {answer_results.get('aggregate_score', 0):.2f}")

    # Evaluate Query Efficiency
    print("\nEvaluating Query Efficiency...")
    efficiency_results = evaluate_query_efficiency(result.generated_sql)

    print(f"  Efficiency Score: {efficiency_results['efficiency_score']:.2f}")
    if efficiency_results['issues']:
        print(f"  Issues Found:")
        for issue in efficiency_results['issues']:
            print(f"    - [{issue['severity']}] {issue['message']}")

    if efficiency_results['recommendations']:
        print(f"  Recommendations:")
        for rec in efficiency_results['recommendations']:
            print(f"    - {rec}")

    # Overall assessment
    print(f"\n{'=' * 80}")
    print("Overall Assessment:")
    print(f"  SQL Correctness: {sql_metric.score:.2f}")
    print(f"  Context Quality: {context_results.get('aggregate_score', 0):.2f}")
    print(f"  Answer Quality: {answer_results.get('aggregate_score', 0):.2f}")
    print(f"  Query Efficiency: {efficiency_results['efficiency_score']:.2f}")

    overall_score = (
        sql_metric.score +
        context_results.get('aggregate_score', 0) +
        answer_results.get('aggregate_score', 0) +
        efficiency_results['efficiency_score']
    ) / 4

    print(f"  Overall Score: {overall_score:.2f}")
    print(f"{'=' * 80}\n")

    # Assert overall quality threshold
    assert overall_score >= EvaluationConfig.DEEPEVAL_THRESHOLD, \
        f"Overall score {overall_score:.2f} below threshold {EvaluationConfig.DEEPEVAL_THRESHOLD}"


@pytest.mark.sql_agent
@pytest.mark.parametrize("difficulty", ["simple", "medium", "complex"])
def test_sql_agent_by_difficulty(difficulty: str, agent_runner):
    """
    Test SQL agent on cases grouped by difficulty.

    This allows you to see performance across difficulty levels.
    """
    filtered_cases = [tc for tc in TEST_CASES if tc.get("difficulty") == difficulty]

    print(f"\n{'=' * 80}")
    print(f"Testing {difficulty.upper()} cases ({len(filtered_cases)} total)")
    print(f"{'=' * 80}\n")

    results = []
    for test_case in filtered_cases:
        result = agent_runner.run(test_case["question"])
        results.append({
            "id": test_case["id"],
            "success": result.error is None,
            "time_ms": result.execution_time_ms,
        })

    success_rate = sum(1 for r in results if r["success"]) / len(results)
    avg_time = sum(r["time_ms"] for r in results) / len(results)

    print(f"\nResults for {difficulty} cases:")
    print(f"  Success Rate: {success_rate * 100:.1f}%")
    print(f"  Average Time: {avg_time:.2f}ms")

    assert success_rate >= 0.8, f"Success rate {success_rate:.1%} below 80% for {difficulty} cases"


@pytest.mark.sql_agent
def test_agent_performance_benchmark(agent_runner):
    """
    Benchmark agent performance across all test cases.

    This gives overall statistics without deep evaluation.
    """
    print(f"\n{'=' * 80}")
    print(f"Performance Benchmark - {len(TEST_CASES)} test cases")
    print(f"{'=' * 80}\n")

    times = []
    successes = 0

    for test_case in TEST_CASES:
        result = agent_runner.run(test_case["question"])
        times.append(result.execution_time_ms)
        if result.error is None:
            successes += 1

    print(f"Results:")
    print(f"  Total Cases: {len(TEST_CASES)}")
    print(f"  Successful: {successes}")
    print(f"  Failed: {len(TEST_CASES) - successes}")
    print(f"  Success Rate: {successes / len(TEST_CASES) * 100:.1f}%")
    print(f"  Average Time: {sum(times) / len(times):.2f}ms")
    print(f"  Min Time: {min(times):.2f}ms")
    print(f"  Max Time: {max(times):.2f}ms")
    print(f"  Total Time: {sum(times) / 1000:.2f}s")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
