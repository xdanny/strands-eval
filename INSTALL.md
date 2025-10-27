# Installation Guide

Choose your preferred installation method. We recommend using **uv** with the **Makefile** for the fastest setup.

## 🚀 Quick Install (Recommended)

```bash
# One-liner setup with Make
make setup && source .venv/bin/activate && make install

# Configure
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Test
make test-simple
```

**Done!** You're ready to evaluate. ✅

---

## Installation Methods

### Method 1: Makefile + uv (Easiest & Fastest ⚡)

**Best for**: Everyone, especially if you want simplicity

```bash
# 1. Setup (creates venv with uv)
make setup

# 2. Activate virtual environment
source .venv/bin/activate  # On Unix/Mac
.venv\Scripts\activate     # On Windows

# 3. Install dependencies
make install

# 4. Configure
cp .env.example .env
# Edit .env with your favorite editor

# 5. Test installation
make check-config
```

**Available Make commands:**
```bash
make help          # Show all commands
make setup         # Initial setup
make install       # Install dependencies
make install-dev   # Install with dev tools
make test          # Run all tests
make test-simple   # Run simple tests
make test-medium   # Run medium tests
make test-complex  # Run complex tests
make benchmark     # Run benchmark
make clean         # Clean generated files
make check-config  # Verify configuration
```

---

### Method 2: uv (Fast 🚀)

**Best for**: Those who want speed and modern Python tooling

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Unix/Mac
# Or: pip install uv
# Or: pipx install uv

# 2. Create virtual environment
uv venv

# 3. Activate virtual environment
source .venv/bin/activate  # On Unix/Mac
.venv\Scripts\activate     # On Windows

# 4. Install project
uv pip install -e .

# Optional: Install with dev dependencies
uv pip install -e ".[dev]"

# 5. Configure
cp .env.example .env

# 6. Test installation
python config.py
```

**Why uv?**
- 10-100x faster than pip
- Better dependency resolution
- Compatible with pip, requirements.txt, pyproject.toml
- Becoming the standard for modern Python projects

---

### Method 3: pip (Traditional)

**Best for**: Conservative setups or CI/CD compatibility

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
source venv/bin/activate  # On Unix/Mac
venv\Scripts\activate     # On Windows

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .

# 5. Configure
cp .env.example .env

# 6. Test installation
python config.py
```

---

## Configuration

### Required Configuration

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Add API key** (at least one):
   ```bash
   # For Gemini (recommended - free tier available)
   GEMINI_API_KEY=your_key_here
   
   # Or for Claude
   ANTHROPIC_API_KEY=your_key_here
   
   # Or for OpenAI
   OPENAI_API_KEY=your_key_here
   ```

3. **Choose model:**
   ```bash
   EVAL_MODEL=gemini-1.5-flash  # Default, fast & cheap
   ```

### Get API Keys

- **Gemini**: https://aistudio.google.com/ (Free tier available!)
- **Claude**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/

### Verify Installation

```bash
# Check configuration
python config.py

# Or with Make
make check-config
```

Expected output:
```
✓ Using model: gemini-1.5-flash (provider: gemini)
```

---

## System Requirements

- **Python**: 3.10 or higher (3.11 recommended)
- **OS**: Linux, macOS, or Windows (WSL recommended)
- **Memory**: 2GB+ RAM recommended
- **Storage**: ~500MB for dependencies

### Check Python Version

```bash
python --version
# Should show: Python 3.10.x or higher
```

---

## Troubleshooting

### "make: command not found"

**Option A**: Install make
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS
xcode-select --install

# Windows
choco install make
```

**Option B**: Use direct commands instead
```bash
# Instead of: make setup
uv venv

# Instead of: make install
uv pip install -e .

# Instead of: make test
pytest tests/test_sql_agent.py -v
```

### "uv: command not found"

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (if needed)
export PATH="$HOME/.cargo/bin:$PATH"

# Restart shell
source ~/.bashrc  # or ~/.zshrc
```

### "Python version too old"

```bash
# Check version
python --version

# Install Python 3.11 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Install Python 3.11 (macOS)
brew install python@3.11

# Use with project
python3.11 -m venv venv
```

### "API Key not set"

```bash
# Make sure .env file exists
ls -la .env

# Check contents
cat .env

# Should contain:
# GEMINI_API_KEY=your_actual_key_here
```

### "Module not found" errors

```bash
# Ensure virtual environment is activated
which python
# Should show: /path/to/.venv/bin/python

# Reinstall dependencies
uv pip install -e .
# or
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "Permission denied" on Makefile

```bash
# Make sure Makefile has correct line endings (Unix)
dos2unix Makefile  # If on Windows/WSL

# Or just use commands directly
uv venv
source .venv/bin/activate
uv pip install -e .
```

---

## Updating

### Update project dependencies

```bash
# With uv
uv pip install --upgrade -e .

# With pip
pip install --upgrade -r requirements.txt
```

### Update to latest package versions

```bash
# Update all packages
uv pip install --upgrade deepeval strands-agents pytest

# Or manually edit pyproject.toml and reinstall
uv pip install -e .
```

---

## Development Setup

If you plan to contribute or develop custom metrics:

```bash
# Install with dev dependencies
make install-dev

# Or manually
uv pip install -e ".[dev]"

# This includes:
# - ipython (better REPL)
# - black (code formatter)
# - ruff (linter)
```

---

## Uninstallation

```bash
# Remove virtual environment
rm -rf .venv

# Or with venv/
rm -rf venv

# Clean generated files
make clean

# Or manually
rm -rf .pytest_cache __pycache__ evaluators/__pycache__
rm evaluation_results.json
```

---

## Next Steps

After installation:

1. ✅ **Verify**: `make check-config`
2. 📖 **Read**: [QUICKSTART.md](QUICKSTART.md)
3. 🧪 **Test**: `make test-simple`
4. 🔧 **Integrate**: Edit `agent/sql_agent_runner.py`
5. 🚀 **Evaluate**: `make test`

---

## Need Help?

- 📚 Full docs: [README.md](README.md)
- ⚡ Quick start: [QUICKSTART.md](QUICKSTART.md)
- 🔧 uv guide: [uv.md](uv.md)
- 🐛 Issues: Open an issue on GitHub

Happy evaluating! 🎯
