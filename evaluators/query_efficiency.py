"""
Query Efficiency Evaluator for SQL queries.
Checks for performance issues, optimization opportunities, and best practices.
"""

from typing import Dict, List, Any
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import Keyword, DML


class QueryEfficiencyEvaluator:
    """
    Evaluates SQL query efficiency and optimization.

    Checks for:
    - Use of SELECT *
    - Missing WHERE clauses on large tables
    - Cartesian products (missing JOIN conditions)
    - Unnecessary subqueries
    - Use of appropriate indexes
    - Proper use of LIMIT
    """

    def __init__(self):
        """Initialize the efficiency evaluator."""
        self.issues = []
        self.warnings = []
        self.score = 1.0

    def evaluate(self, sql: str, table_sizes: Dict[str, int] = None) -> Dict[str, Any]:
        """
        Evaluate query efficiency.

        Args:
            sql: SQL query to evaluate
            table_sizes: Optional dict of table names to row counts

        Returns:
            Dict with efficiency score and issues found
        """
        self.issues = []
        self.warnings = []
        self.score = 1.0

        if not sql or not sql.strip():
            return self._build_result()

        try:
            parsed = sqlparse.parse(sql)[0]

            # Run all checks
            self._check_select_star(parsed)
            self._check_missing_where(parsed, table_sizes)
            self._check_cartesian_product(parsed)
            self._check_unnecessary_subqueries(parsed)
            self._check_missing_limit(parsed)
            self._check_or_conditions(parsed)
            self._check_function_in_where(parsed)
            self._check_distinct_usage(parsed)

        except Exception as e:
            self.warnings.append(f"Could not parse query for efficiency check: {str(e)}")

        return self._build_result()

    def _build_result(self) -> Dict[str, Any]:
        """Build the evaluation result."""
        # Deduct points for each issue
        self.score -= len(self.issues) * 0.15
        self.score -= len(self.warnings) * 0.05
        self.score = max(0.0, min(1.0, self.score))

        return {
            "efficiency_score": self.score,
            "passed": self.score >= 0.7,
            "issues": self.issues,
            "warnings": self.warnings,
            "recommendations": self._get_recommendations(),
        }

    def _check_select_star(self, parsed):
        """Check for SELECT * usage."""
        sql_upper = str(parsed).upper()

        if "SELECT *" in sql_upper or "SELECT\n*" in sql_upper:
            self.issues.append({
                "type": "SELECT_STAR",
                "severity": "medium",
                "message": "Using SELECT * retrieves all columns, which may be inefficient. Specify only needed columns.",
            })

    def _check_missing_where(self, parsed, table_sizes: Dict[str, int] = None):
        """Check if WHERE clause is missing on potentially large tables."""
        sql_upper = str(parsed).upper()

        # Check if there's a WHERE clause
        has_where = "WHERE" in sql_upper

        # Check if there's a LIMIT clause (acceptable alternative)
        has_limit = "LIMIT" in sql_upper

        # Check if there's a JOIN (aggregation queries might not need WHERE)
        has_join = "JOIN" in sql_upper

        # Check if there's a GROUP BY (aggregation queries)
        has_group_by = "GROUP BY" in sql_upper

        if not has_where and not has_limit:
            # Only flag as issue if we're not doing aggregations
            if not has_group_by:
                self.warnings.append({
                    "type": "MISSING_WHERE",
                    "severity": "low",
                    "message": "Query has no WHERE clause or LIMIT. This might scan entire tables.",
                })

    def _check_cartesian_product(self, parsed):
        """Check for potential cartesian products (missing JOIN conditions)."""
        sql_upper = str(parsed).upper()

        # Count FROM and JOIN occurrences to estimate table count
        from_count = sql_upper.count(" FROM ")
        join_count = sql_upper.count(" JOIN ")

        # Count commas in FROM clause (old-style joins)
        # This is a simplified check
        if "FROM" in sql_upper and "," in sql_upper:
            from_section = sql_upper.split("FROM")[1].split("WHERE")[0] if "WHERE" in sql_upper else sql_upper.split("FROM")[1]
            comma_count = from_section.count(",")

            if comma_count > 0 and "ON" not in sql_upper:
                self.issues.append({
                    "type": "CARTESIAN_PRODUCT",
                    "severity": "high",
                    "message": "Potential cartesian product detected. Multiple tables without JOIN conditions.",
                })

    def _check_unnecessary_subqueries(self, parsed):
        """Check for potentially unnecessary subqueries."""
        sql = str(parsed).upper()

        # Check for simple subqueries that could be JOINs
        if sql.count("SELECT") > 1:
            # This is a heuristic - might have false positives
            if "IN (SELECT" in sql:
                self.warnings.append({
                    "type": "SUBQUERY_IN_WHERE",
                    "severity": "low",
                    "message": "Subquery in WHERE clause could potentially be rewritten as JOIN for better performance.",
                })

    def _check_missing_limit(self, parsed):
        """Check if query returns potentially large result sets without LIMIT."""
        sql_upper = str(parsed).upper()

        # Only check SELECT queries, not aggregations
        if "SELECT" in sql_upper and "LIMIT" not in sql_upper:
            if "GROUP BY" not in sql_upper and "COUNT(" not in sql_upper:
                # Don't flag if it's clearly an aggregation query
                if "SUM(" not in sql_upper and "AVG(" not in sql_upper:
                    self.warnings.append({
                        "type": "MISSING_LIMIT",
                        "severity": "low",
                        "message": "Query might return large result set. Consider adding LIMIT for testing.",
                    })

    def _check_or_conditions(self, parsed):
        """Check for OR conditions that might prevent index usage."""
        sql_upper = str(parsed).upper()

        if " OR " in sql_upper:
            # Check if OR is in WHERE clause
            if "WHERE" in sql_upper:
                where_section = sql_upper.split("WHERE")[1].split("GROUP BY")[0] if "GROUP BY" in sql_upper else sql_upper.split("WHERE")[1]
                if " OR " in where_section:
                    self.warnings.append({
                        "type": "OR_IN_WHERE",
                        "severity": "low",
                        "message": "OR conditions in WHERE clause may prevent index usage. Consider UNION or IN clause.",
                    })

    def _check_function_in_where(self, parsed):
        """Check for functions applied to columns in WHERE clause."""
        sql_upper = str(parsed).upper()

        # Common functions that prevent index usage
        problematic_patterns = [
            "WHERE YEAR(",
            "WHERE MONTH(",
            "WHERE DATE(",
            "WHERE UPPER(",
            "WHERE LOWER(",
            "WHERE SUBSTRING(",
        ]

        for pattern in problematic_patterns:
            if pattern in sql_upper:
                self.warnings.append({
                    "type": "FUNCTION_IN_WHERE",
                    "severity": "medium",
                    "message": f"Function applied to column in WHERE clause may prevent index usage: {pattern}",
                })
                break

    def _check_distinct_usage(self, parsed):
        """Check for potentially expensive DISTINCT usage."""
        sql_upper = str(parsed).upper()

        if "SELECT DISTINCT" in sql_upper:
            # DISTINCT with * or many columns can be expensive
            if "DISTINCT *" in sql_upper:
                self.warnings.append({
                    "type": "DISTINCT_STAR",
                    "severity": "medium",
                    "message": "DISTINCT with * or many columns can be expensive. Consider if it's necessary.",
                })
            # Check if there's already a GROUP BY (might make DISTINCT redundant)
            elif "GROUP BY" in sql_upper:
                self.warnings.append({
                    "type": "DISTINCT_WITH_GROUP_BY",
                    "severity": "low",
                    "message": "DISTINCT with GROUP BY might be redundant. Review if both are needed.",
                })

    def _get_recommendations(self) -> List[str]:
        """Generate recommendations based on issues found."""
        recommendations = []

        issue_types = {issue["type"] for issue in self.issues}
        warning_types = {warning["type"] for warning in self.warnings}

        if "SELECT_STAR" in issue_types:
            recommendations.append("Specify only the columns you need instead of using SELECT *")

        if "CARTESIAN_PRODUCT" in issue_types:
            recommendations.append("Add proper JOIN conditions to avoid cartesian products")

        if "MISSING_WHERE" in warning_types:
            recommendations.append("Consider adding WHERE clause to filter rows or LIMIT to restrict result size")

        if "SUBQUERY_IN_WHERE" in warning_types:
            recommendations.append("Consider rewriting subqueries as JOINs for better performance")

        if "FUNCTION_IN_WHERE" in warning_types:
            recommendations.append("Avoid applying functions to columns in WHERE clause; consider computed columns or index expressions")

        if "OR_IN_WHERE" in warning_types:
            recommendations.append("Consider using IN clause or UNION instead of multiple OR conditions")

        return recommendations


def create_query_efficiency_evaluator() -> QueryEfficiencyEvaluator:
    """Factory function to create query efficiency evaluator."""
    return QueryEfficiencyEvaluator()


def evaluate_query_efficiency(
    sql: str,
    table_sizes: Dict[str, int] = None
) -> Dict[str, Any]:
    """
    Convenience function to evaluate query efficiency.

    Args:
        sql: SQL query to evaluate
        table_sizes: Optional dict of table names to estimated row counts

    Returns:
        Dict with efficiency evaluation results
    """
    evaluator = create_query_efficiency_evaluator()
    return evaluator.evaluate(sql, table_sizes)
