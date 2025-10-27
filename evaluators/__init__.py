"""
Evaluators module for SQL agent evaluation.

This module provides comprehensive evaluation metrics for:
- SQL query correctness
- Context retrieval quality (RAG)
- Answer quality and faithfulness
- Query efficiency and optimization
"""

from .sql_correctness import create_sql_correctness_metric, SqlCorrectnessMetric
from .context_retrieval import (
    ContextRetrievalEvaluator,
    create_contextual_relevancy_metric,
    create_contextual_recall_metric,
    create_contextual_precision_metric,
)
from .answer_quality import (
    AnswerQualityEvaluator,
    create_answer_relevancy_metric,
    create_faithfulness_metric,
    create_hallucination_metric,
    evaluate_sql_answer_quality,
)
from .query_efficiency import (
    QueryEfficiencyEvaluator,
    create_query_efficiency_evaluator,
    evaluate_query_efficiency,
)

__all__ = [
    # SQL Correctness
    "create_sql_correctness_metric",
    "SqlCorrectnessMetric",
    # Context Retrieval
    "ContextRetrievalEvaluator",
    "create_contextual_relevancy_metric",
    "create_contextual_recall_metric",
    "create_contextual_precision_metric",
    # Answer Quality
    "AnswerQualityEvaluator",
    "create_answer_relevancy_metric",
    "create_faithfulness_metric",
    "create_hallucination_metric",
    "evaluate_sql_answer_quality",
    # Query Efficiency
    "QueryEfficiencyEvaluator",
    "create_query_efficiency_evaluator",
    "evaluate_query_efficiency",
]
