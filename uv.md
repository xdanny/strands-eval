# Using UV with Strands Eval Framework

This project is configured to work seamlessly with [uv](https://github.com/astral-sh/uv), the blazingly fast Python package installer and resolver.

## Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 Better dependency resolution
- 🎯 Drop-in replacement for pip
- 📦 Works with existing `requirements.txt` and `pyproject.toml`

## Installation

### Install uv

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with pipx
pipx install uv

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Project with uv

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # Unix
.venv\Scripts\activate     # Windows

# Install project dependencies
uv pip install -e .

# Or install with dev dependencies
uv pip install -e ".[dev]"
```

## Using uv Commands

### Install packages

```bash
# Install from pyproject.toml
uv pip install -e .

# Install a single package
uv pip install deepeval

# Install from requirements.txt (still supported)
uv pip install -r requirements.txt

# Sync exact dependencies
uv pip sync requirements.txt
```

### Run commands

```bash
# Run Python scripts
uv run python config.py

# Run pytest
uv run pytest tests/test_sql_agent.py -v

# Run the evaluation runner
uv run python run_evaluation.py --difficulty simple
```

### Upgrade packages

```bash
# Upgrade all packages
uv pip install --upgrade -e .

# Upgrade specific package
uv pip install --upgrade deepeval
```

## Using Makefile (Easiest)

We've included a Makefile for common tasks:

```bash
# Initial setup
make setup

# Install dependencies
make install

# Run tests
make test
make test-simple
make test-medium
make test-complex
make benchmark

# Clean generated files
make clean

# Check configuration
make check-config
```

## Using uv with MCP Server

Since you have `strands-agents-mcp-server` in your `.mcp.json`, you can run it with uv:

```bash
# Run MCP server via uv
uvx strands-agents-mcp-server

# This is what's configured in .mcp.json
```

## Performance Comparison

```bash
# Traditional pip
time pip install -r requirements.txt
# ~30-60 seconds

# With uv
time uv pip install -r requirements.txt
# ~2-5 seconds ⚡
```

## Lock Files (Optional)

If you want reproducible builds:

```bash
# Generate uv.lock file
uv pip compile pyproject.toml -o requirements.lock

# Install from lock file
uv pip sync requirements.lock
```

## Migration from pip

Everything still works with pip if you prefer:

```bash
# These all still work:
pip install -r requirements.txt
pip install -e .
python -m venv venv
```

## Troubleshooting

### uv not found after installation

```bash
# Add to your PATH (usually automatic)
export PATH="$HOME/.cargo/bin:$PATH"

# Or restart your shell
```

### Virtual environment issues

```bash
# Remove and recreate
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Package conflicts

```bash
# uv has better dependency resolution
# If you hit conflicts with pip, try:
uv pip install -e . --resolution highest
```

## Best Practices

1. **Use uv for speed** during development
2. **Use make commands** for convenience
3. **Keep requirements.txt** for CI/CD compatibility
4. **Use pyproject.toml** as source of truth
5. **Test with both** pip and uv occasionally

## Quick Reference

```bash
# Setup (first time)
make setup
source .venv/bin/activate
make install
cp .env.example .env

# Daily workflow
source .venv/bin/activate
make test-simple          # Quick test
make test                 # Full test suite

# Add new dependency
uv pip install <package>
# Then add to pyproject.toml [dependencies]

# Update all packages
uv pip install --upgrade -e .
```

## Learn More

- [uv Documentation](https://github.com/astral-sh/uv)
- [uv vs pip Benchmarks](https://github.com/astral-sh/uv#benchmarks)
- [pyproject.toml Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

---

**TL;DR**: Just use `make setup` then `make install` and you're good to go! 🚀
