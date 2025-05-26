# 📦 Installation Guide

## 🚀 Option 1: UV Package Manager (Recommended)

UV is a fast Python package manager. Here's how to install and use it:

### Install UV

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.sh | iex"

# Alternative: Using pip
pip install uv
```

### Setup Project with UV

```bash
# 1. Clone/navigate to project directory
cd A2A_learning

# 2. Create virtual environment and install dependencies
uv sync

# 3. Setup environment variables
cp .env.example .env
# Edit .env and add your Gemini API key

# 4. Run the project
uv run python servers/assistant_server.py
```

## 📋 Option 2: Traditional pip/venv

If you prefer traditional Python package management:

### Requirements File

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env and add your Gemini API key
```

### Create requirements.txt

```bash
# Generate requirements from pyproject.toml
pip install build
python -m build --wheel
pip install dist/*.whl --dry-run > requirements.txt
```

## 🔧 Development Setup

For development with additional tools:

```bash
# Install with development dependencies
uv sync --extra dev

# Or with pip:
pip install -e ".[dev]"
```

## ✅ Verify Installation

```bash
# Test that everything works
uv run python -c "import google.generativeai; print('✅ Google AI installed')"
uv run python -c "import fastapi; print('✅ FastAPI installed')"
uv run python -c "from agents import BaseAgent; print('✅ Agents package working')"
```

## 🆘 Troubleshooting

**UV not found after installation:**
```bash
# Add UV to your PATH
export PATH="$HOME/.cargo/bin:$PATH"
# Or restart your terminal
```

**Python version issues:**
```bash
# UV will automatically use the right Python version
uv python install 3.9  # If you need Python 3.9+
```

**Package conflicts:**
```bash
# Clean and reinstall
rm -rf .venv uv.lock
uv sync
```

## 📚 UV vs pip Comparison

| Feature | UV | pip |
|---------|----|----|
| Speed | ⚡ Very Fast | 🐌 Slower |
| Lock files | ✅ Automatic | ❌ Manual |
| Virtual envs | ✅ Automatic | ❌ Manual |
| Cross-platform | ✅ Yes | ✅ Yes |
| Learning curve | 📈 Easy | 📈 Familiar |

**Recommendation**: Use UV for faster, more reliable dependency management!