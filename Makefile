# Makefile for Strands SQL Agent Evaluation Framework

.PHONY: help install install-dev test test-simple test-medium test-complex benchmark clean setup

help:
	@echo "Strands SQL Agent Evaluation Framework"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup          - Initial setup with uv (recommended)"
	@echo "  make install        - Install dependencies with uv"
	@echo "  make install-dev    - Install with dev dependencies"
	@echo "  make test           - Run all tests"
	@echo "  make test-simple    - Run simple test cases only"
	@echo "  make test-medium    - Run medium test cases only"
	@echo "  make test-complex   - Run complex test cases only"
	@echo "  make benchmark      - Run performance benchmark"
	@echo "  make clean          - Clean generated files"
	@echo "  make check-config   - Verify configuration"

setup:
	@echo "Setting up environment with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "Installing uv..."; curl -LsSf https://astral.sh/uv/install.sh | sh; }
	uv venv
	@echo ""
	@echo "✓ Virtual environment created in .venv/"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate venv: source .venv/bin/activate"
	@echo "  2. Install deps:  make install"
	@echo "  3. Configure:     cp .env.example .env (then edit)"
	@echo "  4. Run tests:     make test-simple"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	pytest tests/test_sql_agent.py -v

test-simple:
	pytest tests/test_sql_agent.py -k "simple" -v

test-medium:
	pytest tests/test_sql_agent.py -k "medium" -v

test-complex:
	pytest tests/test_sql_agent.py -k "complex" -v

benchmark:
	pytest tests/test_sql_agent.py -k "benchmark" -v

check-config:
	python config.py

clean:
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf evaluators/__pycache__
	rm -rf agent/__pycache__
	rm -rf tests/__pycache__
	rm -f evaluation_results.json
	rm -rf .deepeval
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
