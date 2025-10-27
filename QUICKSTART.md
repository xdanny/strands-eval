# Quick Start Guide

Get up and running with the SQL Agent Evaluation Framework in 5 minutes!

## Step 1: Install (2 minutes)

### Using Makefile (Easiest! ⚡)

```bash
# One command setup
make setup

# Activate and install
source .venv/bin/activate
make install
```

### Using uv (Recommended - Much Faster!)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix
# Or: pip install uv

# Navigate to project
cd strands-eval

# Create venv and install (super fast!)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### Using pip (Alternative)

```bash
cd strands-eval
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 2: Configure (1 minute)

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key (get one free at https://aistudio.google.com/):

```bash
GEMINI_API_KEY=your_key_here
EVAL_MODEL=gemini-1.5-flash
```

## Step 3: Test Setup (30 seconds)

```bash
# Check configuration
python config.py
```

You should see:
```
✓ Using model: gemini-1.5-flash (provider: gemini)
```

## Step 4: Run Your First Evaluation (1 minute)

```bash
# Using Makefile (easiest)
make test-simple

# Or using the runner
python run_evaluation.py --difficulty simple

# Or use pytest directly
pytest tests/test_sql_agent.py -k "simple_dau_001" -v
```

## Step 5: Review Results

Results are printed to console and saved to `evaluation_results.json`.

Example output:
```
Test Case: simple_dau_001
Question: What was the number of daily active users yesterday?
Difficulty: simple
================================================================================

✓ SQL Correctness Score: 0.85
  Contextual Relevancy: 0.80
  Contextual Recall: 0.85
  Answer Relevancy: 0.90
  Faithfulness: 0.88
  Efficiency Score: 0.92

Overall Assessment:
  SQL Correctness: 0.85
  Context Quality: 0.83
  Answer Quality: 0.86
  Query Efficiency: 0.92
  Overall Score: 0.87
```

## Next Steps

### 1. Implement Your Agent

The framework currently uses a placeholder agent. Replace it with your actual implementation:

```python
# Edit agent/sql_agent_runner.py

class MyCustomSqlAgent(SqlAgentRunner):
    def __init__(self, schema_path, agent_config=None):
        super().__init__(schema_path, agent_config)
        # Initialize your Strands agent here
        self.agent = initialize_your_agent()

    def _retrieve_context(self, question: str):
        # Use your MCP tools
        return self.mcp_client.call_tool("search_schema", {"query": question})

    def _generate_sql(self, question: str, contexts: list):
        # Use your agent
        prompt = self._build_prompt(question, contexts)
        return self.agent.run(prompt)
```

### 2. Run Full Evaluation

```bash
# Run all 20 test cases
python run_evaluation.py

# Run by difficulty
python run_evaluation.py --difficulty medium
python run_evaluation.py --difficulty complex

# Run performance benchmark only (faster)
python run_evaluation.py --benchmark
```

### 3. Try Different Models

```bash
# Try Gemini Pro (more accurate)
python run_evaluation.py --model gemini-1.5-pro

# Try Claude Sonnet (best accuracy, requires ANTHROPIC_API_KEY)
python run_evaluation.py --model claude-3-5-sonnet-20241022

# Try local Ollama (free, requires ollama running)
python run_evaluation.py --model ollama/qwen2.5-coder
```

### 4. Add Custom Test Cases

Edit `datasets/test_cases.json`:

```json
{
  "id": "my_test_001",
  "difficulty": "simple",
  "question": "How many users signed up today?",
  "expected_sql": "SELECT COUNT(*) FROM users WHERE DATE(created_at) = CURRENT_DATE",
  "expected_context": [
    "users table has created_at timestamp"
  ],
  "sql_criteria": {
    "must_use_tables": ["users"],
    "must_use_columns": ["created_at"]
  }
}
```

## Common Issues

### "GEMINI_API_KEY not set"

Make sure `.env` file exists and has your API key:
```bash
GEMINI_API_KEY=your_actual_key_here
```

### "Module not found"

Make sure you're in the project root:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Model Comparison

Show all available models and recommendations:
```bash
python run_evaluation.py --show-models
```

## What Gets Evaluated?

For each test case, the framework evaluates:

1. **SQL Correctness** (0-1 score)
   - Syntax validity ✓
   - Correct tables/columns ✓
   - Answers the question ✓
   - Efficient query ✓

2. **Context Retrieval** (0-1 score)
   - Retrieved relevant context? ✓
   - Got all necessary info? ✓
   - How much noise? ✓

3. **Answer Quality** (0-1 score)
   - Answer relevant to question? ✓
   - Factually accurate? ✓
   - No hallucinations? ✓

4. **Query Efficiency** (0-1 score)
   - No SELECT * ✓
   - Proper WHERE clauses ✓
   - Correct JOIN usage ✓
   - Optimized patterns ✓

## Pro Tips

1. **Start with simple cases** - Validate your setup works
2. **Use gemini-1.5-flash for dev** - Fast and cheap (~$0.075/1M tokens)
3. **Use claude-3-5-sonnet for CI** - Most accurate for final validation
4. **Check the reason field** - When tests fail, read the detailed reasoning
5. **Monitor API costs** - Track usage, especially with Claude/GPT-4

## Example Workflow

```bash
# 1. Quick check during development
python run_evaluation.py --difficulty simple --verbose

# 2. Full test before commit
python run_evaluation.py

# 3. Compare models
python run_evaluation.py --model gemini-1.5-flash
python run_evaluation.py --model gemini-1.5-pro

# 4. Generate report for stakeholders
pytest tests/test_sql_agent.py --json-report --json-report-file=report.json
```

## Need Help?

- Check [README.md](README.md) for detailed documentation
- Review [test_cases.json](datasets/test_cases.json) for example test cases
- Look at [sql_agent_runner.py](agent/sql_agent_runner.py) for integration examples
- Check DeepEval docs: https://docs.confident-ai.com/

## What's Next?

1. ✅ Framework setup complete
2. 🔧 Integrate your SQL agent
3. 🧪 Run evaluations
4. 📊 Review metrics
5. 🔄 Iterate and improve
6. 🚀 Deploy to CI/CD

Happy evaluating! 🎯
