#!/usr/bin/env python3
"""
Convenience script to run evaluations.

Usage:
    python run_evaluation.py                    # Run all tests
    python run_evaluation.py --difficulty simple  # Run only simple cases
    python run_evaluation.py --verbose           # Verbose output
    python run_evaluation.py --model gemini-1.5-pro  # Use specific model
"""

import sys
import argparse
import subprocess
from pathlib import Path

from config import EvaluationConfig, print_model_recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Run SQL Agent Evaluation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--difficulty",
        choices=["simple", "medium", "complex"],
        help="Run only tests of specific difficulty",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show all logs)",
    )

    parser.add_argument(
        "--model",
        help="Override EVAL_MODEL from config (e.g., gemini-1.5-flash, claude-3-5-sonnet-20241022)",
    )

    parser.add_argument(
        "--show-models",
        action="store_true",
        help="Show available model options and exit",
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run only performance benchmark (faster)",
    )

    parser.add_argument(
        "--test-id",
        help="Run only a specific test case by ID",
    )

    args = parser.parse_args()

    # Show model recommendations and exit
    if args.show_models:
        print_model_recommendations()
        return 0

    # Build pytest command
    pytest_args = ["pytest", "tests/test_sql_agent.py"]

    # Add verbosity
    if args.verbose:
        pytest_args.extend(["-v", "-s"])
    else:
        pytest_args.append("-v")

    # Filter by difficulty
    if args.difficulty:
        pytest_args.extend(["-k", args.difficulty])

    # Run only benchmark
    if args.benchmark:
        pytest_args.extend(["-k", "benchmark"])

    # Run specific test
    if args.test_id:
        pytest_args.extend(["-k", args.test_id])

    # Add JSON report
    pytest_args.extend([
        "--json-report",
        "--json-report-file=evaluation_results.json",
    ])

    # Set model override if provided
    env = None
    if args.model:
        import os
        env = os.environ.copy()
        env["EVAL_MODEL"] = args.model
        print(f"Using model: {args.model}")

    # Validate configuration
    try:
        EvaluationConfig.validate_config()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nMake sure you've created .env file with required API keys.")
        print("See .env.example for reference.")
        return 1

    # Run pytest
    print(f"\nRunning evaluations...")
    print(f"Command: {' '.join(pytest_args)}\n")

    result = subprocess.run(pytest_args, env=env)

    # Print results location
    if result.returncode == 0:
        print(f"\n✅ Evaluation completed successfully!")
        print(f"📊 Results saved to: evaluation_results.json")
    else:
        print(f"\n❌ Evaluation failed with errors")
        print(f"📊 Results saved to: evaluation_results.json")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
