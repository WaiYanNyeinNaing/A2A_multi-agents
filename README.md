# A2A Multi-Agent System

A clean, modular implementation of the **A2A (Agent-to-Agent) Protocol** for inter-agent communication using Google's Gemini AI models and the Google Agent Development Kit (ADK).

## 🏗️ System Architecture

### Core Components

```
A2A_learning/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base class with common functionality
│   ├── assistant_agent.py # Main orchestrator agent
│   ├── image_agent.py     # Image generation specialist
│   └── writing_agent.py   # Content writing specialist
├── core/                  # A2A protocol infrastructure
│   ├── a2a_client.py     # Agent discovery and communication
│   └── a2a_server.py     # A2A server wrapper
├── servers/              # Server runners
│   ├── assistant_server.py
│   ├── image_server.py
│   └── writing_server.py
├── tools/               # Utilities and interfaces
│   └── interactive_interface.py
└── examples/           # Example implementations
    └── research_agent_openai_sdk.py
```

### Agent Hierarchy

- **BaseAgent**: Abstract base class providing common functionality
  - **AssistantAgent**: Orchestrator that coordinates multiple agents
  - **ImageAgent**: Specialized for image generation using Imagen
  - **WritingAgent**: Specialized for content creation and editing
  - **ResearchAgent**: Specialized for web research and data collection
  - **ReportAgent**: Specialized for creating comprehensive reports

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Install UV package manager (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (creates virtual environment automatically)
uv sync

# Setup environment variables
cp .env.example .env
# Edit .env and add your Gemini API key from https://ai.google.dev/
```

**Alternative (Traditional pip):**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Start Agent Servers

```bash
# Terminal 1: Assistant Agent (Orchestrator)
uv run python servers/assistant_server.py

# Terminal 2: Image Generation Agent
uv run python servers/image_server.py

# Terminal 3: Writing Agent
uv run python servers/writing_server.py

# Terminal 4: Research Agent (Web Search & Data Collection)
uv run python servers/research_server.py

# Terminal 5: Report Writing Agent (Comprehensive Reports)
uv run python servers/report_server.py
```

### 3. Use Interactive Interface

```bash
uv run python tools/interactive_interface.py
```

## 🔄 A2A Protocol Flow

### Single Agent Request
1. Client discovers agent via Agent Card (`/.well-known/agent.json`)
2. Client sends JSON-RPC `tasks/send` request
3. Agent processes request using specialized tools
4. Agent returns task with artifacts
5. Client extracts and processes results

### Multi-Agent Orchestration
1. User sends complex request to Assistant Agent
2. Assistant analyzes request to determine needed services
3. Assistant makes A2A calls to specialized agents
4. Assistant aggregates results from multiple agents
5. Assistant returns comprehensive response

## 🛠️ Key Features

### Clean Architecture
- **Modular Design**: Separated concerns with clear boundaries
- **Inheritance Hierarchy**: Common functionality in base classes
- **Standardized Naming**: Consistent file and class naming conventions
- **Type Safety**: Full type hints throughout

### A2A Protocol Benefits
- **Auto-discovery**: Agents advertise capabilities via Agent Cards
- **Async Processing**: Non-blocking task execution
- **Multi-format Output**: Text, images, structured data
- **Error Handling**: Graceful failure handling with fallbacks
- **Result Persistence**: Automatic saving of generated content

### Agent Capabilities
- **Image Generation**: High-quality images using Imagen 3.0
- **Content Writing**: Articles, summaries, content editing
- **Web Research**: Real-time web search and data collection
- **Report Writing**: Comprehensive reports in multiple formats
- **Request Analysis**: Intelligent routing of complex requests
- **Coordination**: Seamless multi-agent task execution

## 📊 Agent Specifications

### Assistant Agent (Port 8000)
- **Type**: Orchestrator
- **Capabilities**: Request analysis, agent coordination, response aggregation
- **Communication**: A2A protocol with specialized agents

### Image Agent (Port 8001)  
- **Type**: Image Generation Specialist
- **Capabilities**: Single/batch image generation, prompt enhancement
- **Model**: Imagen 3.0 Generate 002

### Writing Agent (Port 8002)
- **Type**: Content Writing Specialist  
- **Capabilities**: Article writing, content creation
- **Styles**: Informative, creative, professional, casual

### Research Agent (Port 8003)
- **Type**: Web Research & Data Collection Specialist
- **Capabilities**: Web search, topic research, fact-checking
- **APIs**: Serper API for real-time web search

### Report Agent (Port 8004)
- **Type**: Report Writing Specialist
- **Capabilities**: Comprehensive reports, format conversion, executive summaries
- **Formats**: Markdown, HTML, slide outlines

## 🔧 Configuration

### Environment Variables
```bash
# Required
GEMINI_API_KEY=your_api_key_here
SERPER_API_KEY=your_serper_api_key_here     # For web search (get from serper.dev)

# Optional (with defaults)
GEMINI_MODEL_NAME=gemini-2.0-flash-exp      # Text generation model
IMAGEN_MODEL_NAME=imagen-3.0-generate-002   # Image generation model
HTTP_PROXY=http://proxy:port                # Proxy if needed

# Agent URLs
IMAGE_AGENT_URL=http://localhost:8001       # Image agent URL
WRITER_AGENT_URL=http://localhost:8002      # Writing agent URL
RESEARCH_AGENT_URL=http://localhost:8003    # Research agent URL
REPORT_AGENT_URL=http://localhost:8004      # Report agent URL
```

### Agent Discovery
Agents expose discovery information at `/.well-known/agent.json`:
```json
{
  "name": "Agent Name",
  "description": "Agent description",
  "url": "http://localhost:port/a2a",
  "capabilities": {...},
  "skills": [...]
}
```

## 🧪 Usage Examples

### Direct Agent Communication
```python
from core import A2AClient

client = A2AClient()

# Image generation
result = await client.send_and_wait(
    "http://localhost:8001", 
    "Generate a beautiful sunset landscape"
)

# Article writing
result = await client.send_and_wait(
    "http://localhost:8002",
    "Write an article about renewable energy"
)

# Web research
result = await client.send_and_wait(
    "http://localhost:8003",
    "Research latest AI developments"
)

# Report writing
result = await client.send_and_wait(
    "http://localhost:8004",
    "Create comprehensive report on climate change"
)
```

### Multi-Agent Coordination
```python
# Send complex request to assistant
result = await client.send_and_wait(
    "http://localhost:8000",
    "Research renewable energy trends and create a comprehensive report with solar panel images"
)
```

### Research Workflows
```python
# Step 1: Research data
research_result = await client.send_and_wait(
    "http://localhost:8003",
    "Research climate change impact on agriculture"
)

# Step 2: Create report from research
report_result = await client.send_and_wait(
    "http://localhost:8004", 
    f"Create comprehensive report: {research_result['data']}"
)
```

## 📁 File Structure Changes

### ✅ Improvements Made:
1. **Consolidated Agents**: Removed duplicate code, created base class
2. **Organized Structure**: Logical directory separation
3. **Standardized Naming**: Consistent file and class names
4. **Removed Duplicates**: Eliminated redundant implementations
5. **Separated Concerns**: Core protocol vs. agent implementations
6. **Moved Examples**: Unrelated code moved to examples directory

### 🗂️ Directory Purpose:
- `agents/`: Clean agent implementations with inheritance
- `core/`: A2A protocol client/server infrastructure  
- `servers/`: Simple server runners for each agent
- `tools/`: Interactive interfaces and utilities
- `examples/`: Example implementations and demos

## 🔄 Migration from Old Structure

Old files have been refactored and consolidated:
- `gemini_assistant_agent.py` → `agents/assistant_agent.py`
- `image_generation_agent.py` → `agents/image_agent.py`  
- `writing_agent.py` → `agents/writing_agent.py`
- `a2a_client.py` → `core/a2a_client.py`
- `run_*_server.py` → `servers/*_server.py`
- `interactive_agent_interface.py` → `tools/interactive_interface.py`
- `research_agent_openai_sdk.py` → `examples/` (unrelated to A2A)

All import statements and references have been updated accordingly.

## 📦 Dependencies & Lock Files

- **`pyproject.toml`**: Project configuration and dependencies (latest versions)
- **`uv.lock`**: Exact dependency versions for reproducible builds (auto-generated)
- **`requirements.txt`**: For traditional pip users

UV automatically creates `uv.lock` for reproducible installations across environments.

## 🎯 Next Steps

1. **Testing**: Add comprehensive unit tests
2. **Authentication**: Implement agent-to-agent security
3. **Persistence**: Add database storage for tasks
4. **Monitoring**: Add logging and metrics
5. **Documentation**: API documentation with examples
6. **Docker**: Containerization for easy deployment