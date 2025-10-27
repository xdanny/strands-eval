# SQL Agent Evaluation Framework

A comprehensive evaluation framework for SQL agents using **Strands**, **DeepEval**, and **MCP tools**. This framework evaluates agents across multiple dimensions: SQL correctness, context retrieval quality, answer quality, and query efficiency.

## Features

- **Multi-Model Support**: Works with Gemini, Claude, OpenAI, and Ollama
- **Comprehensive Metrics**: 4 categories of evaluation metrics
- **20 Test Cases**: Covers simple to complex SQL scenarios
- **Analytics Schema**: Realistic data warehouse schema for testing
- **CI/CD Ready**: Designed for automated testing pipelines
- **Agentcore Integration**: Built-in observability hooks

## Quick Start

### 1. Installation

#### Using Makefile (Easiest! ⚡)

```bash
# One command to set everything up
make setup

# Activate environment
source .venv/bin/activate

# Install dependencies
make install

# Done! Now configure your .env file
cp .env.example .env
```

#### Using uv (Recommended - Fast!)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix
# Or: pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Using pip (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API key(s):

```bash
# Choose your preferred model
EVAL_MODEL=gemini-1.5-flash  # Cost-effective default

# Add corresponding API key
GEMINI_API_KEY=your_key_here
```

**Model Options:**

| Model | Best For | Cost | Speed |
|-------|----------|------|-------|
| `gemini-1.5-flash` | CI/CD, cost-sensitive | ⭐⭐⭐ | ⚡⚡⚡ |
| `gemini-1.5-pro` | Balanced accuracy/cost | ⭐⭐ | ⚡⚡ |
| `claude-3-5-sonnet-20241022` | Best accuracy | ⭐ | ⚡ |
| `ollama/qwen2.5-coder` | Local/free | Free | ⚡ (GPU) |

### 3. Implement Your Agent

Edit `agent/sql_agent_runner.py` to integrate your actual SQL agent:

```python
from agent.sql_agent_runner import SqlAgentRunner

class MyCustomSqlAgent(SqlAgentRunner):
    def _retrieve_context(self, question: str):
        # Use your MCP tools or RAG system
        return self.mcp_client.search_schema(question)

    def _generate_sql(self, question: str, contexts: list):
        # Use your Strands agent to generate SQL
        return self.agent.run(prompt)
```

### 4. Run Evaluations

#### Using Makefile (Easiest!)

```bash
# Run simple tests
make test-simple

# Run all tests
make test

# Run by difficulty
make test-medium
make test-complex

# Run benchmark only
make benchmark

# Check configuration
make check-config
```

#### Using pytest directly

```bash
# Run all tests
pytest tests/test_sql_agent.py -v

# Run specific difficulty level
pytest tests/test_sql_agent.py -k "simple" -v

# Run with detailed output
pytest tests/test_sql_agent.py -v -s

# Generate JSON report
pytest tests/test_sql_agent.py --json-report --json-report-file=results.json
```

## Evaluation Metrics

### 1. SQL Correctness (G-Eval)

Custom metric evaluating:
- ✅ Syntax validity
- ✅ Semantic correctness (right tables/columns)
- ✅ Logic correctness (answers the question)
- ✅ Query efficiency

**File**: `evaluators/sql_correctness.py`

### 2. Context Retrieval (RAG)

Evaluates context quality using:
- **Contextual Relevancy**: Is retrieved context relevant?
- **Contextual Recall**: Did we get all necessary info?
- **Contextual Precision**: How much retrieved context is useful?

**File**: `evaluators/context_retrieval.py`

### 3. Answer Quality

Evaluates final answers using:
- **Answer Relevancy**: Does answer address the question?
- **Faithfulness**: Is answer grounded in context?
- **Hallucination**: Does answer contain fabrications?

**File**: `evaluators/answer_quality.py`

### 4. Query Efficiency

Static analysis checking for:
- SELECT * usage
- Missing WHERE clauses
- Cartesian products
- Function in WHERE (prevents index usage)
- Unnecessary subqueries

**File**: `evaluators/query_efficiency.py`

## Test Dataset

20 test cases across 3 difficulty levels:

### Simple (5 cases)
- Daily active users
- User signup counts
- Product listings

### Medium (9 cases)
- Revenue by category
- Inactive users
- Session analytics
- Geographic analysis
- Conversion rates

### Complex (6 cases)
- Cohort retention analysis
- Conversion funnels
- Marketing attribution
- Churn analysis
- LTV calculations
- Product affinity (market basket)

**File**: `datasets/test_cases.json`

## Schema

Analytics data warehouse with 5 tables:

- **events**: User interaction tracking
- **users**: User dimension with demographics
- **sessions**: Session metrics and attribution
- **products**: Product catalog
- **purchases**: Transaction data

**File**: `datasets/analytics_schema.json`

## Project Structure

```
strands-eval/
├── datasets/
│   ├── analytics_schema.json      # Sample schema
│   ├── test_cases.json            # 20 evaluation test cases
│   └── golden_contexts.json       # Expected RAG contexts
├── evaluators/
│   ├── sql_correctness.py         # Custom G-Eval metric
│   ├── context_retrieval.py       # RAG evaluation
│   ├── answer_quality.py          # Answer metrics
│   └── query_efficiency.py        # Performance checks
├── agent/
│   └── sql_agent_runner.py        # Your agent wrapper
├── tests/
│   └── test_sql_agent.py          # Main test suite
├── config.py                       # Configuration management
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Configuration Options

### Model Configuration

```python
# In config.py
EVAL_MODEL = "gemini-1.5-flash"     # Which model to use
DEEPEVAL_THRESHOLD = 0.7            # Minimum passing score
DEEPEVAL_VERBOSE = True             # Include reasoning
```

### Changing Models

To test with different models:

```bash
# Try Gemini Flash (fast & cheap)
export EVAL_MODEL=gemini-1.5-flash
pytest tests/test_sql_agent.py

# Try Claude Sonnet (most accurate)
export EVAL_MODEL=claude-3-5-sonnet-20241022
pytest tests/test_sql_agent.py

# Try local Ollama (free)
export EVAL_MODEL=ollama/qwen2.5-coder
pytest tests/test_sql_agent.py
```

## Integration with Agentcore

The framework includes hooks for Agentcore observability:

```python
# In config.py
AGENTCORE_API_KEY=your_key
AGENTCORE_PROJECT_ID=sql-agent-eval
```

Agentcore will track:
- Execution traces
- Metric scores
- Performance data
- Error rates

## CI/CD Integration

### GitHub Actions Example

```yaml
name: SQL Agent Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run evaluations
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          EVAL_MODEL: gemini-1.5-flash
        run: |
          pytest tests/test_sql_agent.py -v --json-report

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: evaluation-results
          path: evaluation_results.json
```

## Extending the Framework

### Adding New Test Cases

Edit `datasets/test_cases.json`:

```json
{
  "id": "new_test_021",
  "difficulty": "medium",
  "question": "Your question here",
  "expected_sql": "SELECT ...",
  "expected_context": ["Context 1", "Context 2"],
  "sql_criteria": {
    "must_use_tables": ["users"],
    "must_join": true
  }
}
```

### Adding Custom Metrics

Create a new metric in `evaluators/`:

```python
from deepeval.metrics import BaseMetric

class MyCustomMetric(BaseMetric):
    def measure(self, test_case):
        # Your evaluation logic
        self.score = ...
```

## Troubleshooting

### "API Key not set" Error

Make sure you've created `.env` file and set the correct API key for your chosen model:

```bash
# For Gemini
GEMINI_API_KEY=your_key

# For Claude
ANTHROPIC_API_KEY=your_key

# For OpenAI
OPENAI_API_KEY=your_key
```

### "Module not found" Error

Ensure you're in the project root and dependencies are installed:

```bash
pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Ollama Connection Error

If using Ollama, ensure the server is running:

```bash
ollama serve
ollama pull qwen2.5-coder:7b
```

## Best Practices

1. **Start Simple**: Test with simple cases first to validate your setup
2. **Use Fast Models for Dev**: Use `gemini-1.5-flash` during development
3. **Use Accurate Models for CI**: Use `claude-3-5-sonnet` for final validation
4. **Monitor Costs**: Track API usage, especially with Claude/GPT-4
5. **Version Your Tests**: Keep test cases in git to track improvements
6. **Review Failures**: Always check `reason` field in failed metrics

## Performance Benchmarks

Expected performance with `gemini-1.5-flash`:

| Metric | Simple | Medium | Complex |
|--------|--------|--------|---------|
| SQL Correctness | 0.85+ | 0.75+ | 0.65+ |
| Context Quality | 0.80+ | 0.75+ | 0.70+ |
| Answer Quality | 0.80+ | 0.75+ | 0.70+ |
| Efficiency | 0.90+ | 0.85+ | 0.80+ |

## References

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [Strands Agents](https://strandsagents.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Agentcore](https://agentcore.ai/)

## License

MIT

## Contributing

Contributions welcome! Please:
1. Add test cases for new scenarios
2. Document new metrics clearly
3. Include examples in README
4. Test with multiple models

## Support

For issues or questions:
- Open an issue in this repository
- Check DeepEval documentation
- Review test outputs for detailed error messages
