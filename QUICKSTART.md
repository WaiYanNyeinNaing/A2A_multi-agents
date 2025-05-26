# 🚀 A2A Multi-Agent System - Quick Start

Get your A2A multi-agent system running in 5 minutes!

## 📋 Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) package manager
- Google Gemini API key

## ⚡ Quick Setup

### 1. Install UV & Dependencies

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies (creates virtual env automatically)
uv sync
```

**Alternative (Traditional pip):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# Get your key from: https://ai.google.dev/
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Start the Agents

Open 5 terminals and run:

```bash
# Terminal 1: Assistant Agent (Orchestrator)
uv run python servers/assistant_server.py

# Terminal 2: Image Generation Agent  
uv run python servers/image_server.py

# Terminal 3: Writing Agent
uv run python servers/writing_server.py

# Terminal 4: Research Agent (Web Search)
uv run python servers/research_server.py

# Terminal 5: Report Writing Agent
uv run python servers/report_server.py
```

### 4. Test the System

```bash
# Terminal 6: Interactive Interface
uv run python tools/interactive_interface.py
```

## 🎯 Quick Tests

**Basic Test:**
1. Choose option `1` (Assistant Agent)
2. Enter: `"Write an article about AI and generate a robot image"`

**Research Test:**
1. Choose option `4` (Research Agent)
2. Enter: `"Latest developments in artificial intelligence 2024"`

**Full Workflow Test:**
1. Choose option `1` (Assistant Agent)
2. Enter: `"Research renewable energy trends and create a comprehensive report with solar panel images"`

Watch the magic happen! ✨

## 📚 What Each Agent Does

- **Assistant (Port 8000)**: Coordinates multiple agents for complex tasks
- **Image Agent (Port 8001)**: Generates images using Google Imagen
- **Writing Agent (Port 8002)**: Creates articles and written content
- **Research Agent (Port 8003)**: Web search and data collection
- **Report Agent (Port 8004)**: Comprehensive reports and documentation

## 🔧 Troubleshooting

**"GEMINI_API_KEY not found"**
- Make sure you copied `.env.example` to `.env`
- Add your actual API key from https://ai.google.dev/

**"Agent offline"**
- Check that all 5 server terminals are running
- Wait a moment for agents to fully start up

**"Import errors"**
- Run `uv sync` to install all dependencies

## 🎉 You're Ready!

Your A2A multi-agent system is now running. Try different prompts and explore the capabilities!

For more details, see the full [README.md](README.md).