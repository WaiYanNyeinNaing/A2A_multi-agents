# A2A Multi-Agent System

A fully operational, production-ready implementation of the **A2A (Agent-to-Agent) Protocol** for intelligent multi-agent coordination using Google's Gemini AI models. Features sequential orchestration, context passing, and real-time coordination across specialized AI agents.

## 🏗️ System Architecture

### Core Components

```
A2A_learning/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base class with common functionality & API integration
│   ├── assistant_agent.py # Main orchestrator with LLM-based intent detection
│   ├── image_agent.py     # Image generation with file-based workflow
│   ├── writing_agent.py   # Content writing specialist
│   ├── research_agent.py  # Web research & data collection
│   └── report_agent.py    # Comprehensive report generation
├── core/                  # A2A protocol infrastructure
│   ├── a2a_client.py     # Agent discovery and communication
│   └── a2a_server.py     # A2A server wrapper
├── servers/              # Server runners
│   ├── assistant_server.py
│   ├── image_server.py
│   ├── writing_server.py
│   ├── research_server.py
│   └── report_server.py
├── tools/               # Utilities and interfaces
│   └── interactive_interface.py
├── test_coordination.py    # Multi-agent workflow testing
├── test_individual_agents.py # Individual agent testing & debugging  
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

### ✨ Latest Updates (v2.0)
- **🎯 Intelligent Orchestration**: LLM-based intent detection automatically routes complex requests to appropriate agents
- **🔄 Sequential Coordination**: Context passing between agents (research → writing → image generation)
- **📊 Real Data Processing**: Extract actual metrics from agent responses (word counts, file sizes, source counts)
- **🎨 File-based Image Workflow**: Generated images saved locally with descriptive filenames and metadata  
- **🏗️ Robust Infrastructure**: Complete BaseAgent implementation with API integration and error handling
- **🧪 Comprehensive Testing**: Full test suite for individual agents and multi-agent workflows

### A2A Protocol Benefits
- **Auto-discovery**: Agents advertise capabilities via Agent Cards
- **Sequential Processing**: Intelligent task orchestration with context passing
- **Multi-format Output**: Text, images, structured data with metadata
- **Error Handling**: Graceful failure handling with detailed error reporting
- **Result Persistence**: Automatic saving of generated content with organized file structure

### Agent Capabilities
- **🎯 Multi-Intent Processing**: Single request → multiple coordinated agent tasks
- **🎨 Image Generation**: High-quality images using Imagen 3.0 with file-based storage
- **✍️ Content Writing**: Context-aware articles based on research data
- **🔍 Web Research**: Real-time web search with 25+ source aggregation
- **📊 Report Generation**: Comprehensive reports in multiple formats
- **🤖 Request Analysis**: LLM-powered intent detection and task planning
- **🔄 Coordination**: Seamless multi-agent workflows with result aggregation

## 📊 Agent Specifications

### Assistant Agent (Port 8000) - 🎯 Orchestrator
- **Capabilities**: LLM-based intent analysis, sequential coordination, result aggregation
- **Features**: Multi-agent workflow planning, context passing, comprehensive reporting
- **Communication**: A2A protocol with all specialized agents

### Image Agent (Port 8001) - 🎨 Visual Creator  
- **Capabilities**: Professional image generation with descriptive naming
- **Features**: File-based workflow, metadata tracking, aspect ratio control
- **Model**: Imagen 3.0 Generate 002 with 1MB+ high-quality outputs

### Writing Agent (Port 8002) - ✍️ Content Creator
- **Capabilities**: Context-aware article writing, title generation, word count tracking
- **Features**: Research-based content creation, multiple writing styles
- **Output**: 800-1500 word articles with proper structure

### Research Agent (Port 8003) - 🔍 Data Collector
- **Capabilities**: Real-time web search, multi-query research, source aggregation  
- **Features**: 25+ source collection, query optimization, result summarization
- **APIs**: Serper API for comprehensive web search

### Report Agent (Port 8004) - 📊 Report Generator
- **Capabilities**: Comprehensive reports, executive summaries, format conversion
- **Features**: Multi-section reports, slide outlines, professional formatting
- **Formats**: Markdown, HTML, structured data output

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

### 🚀 Interactive Interface (Recommended)
```bash
uv run python tools/interactive_interface.py
```
**Example requests:**
- *"Research Champions League final teams, write article, include visual"*
- *"Create comprehensive climate change report with data visualizations"*  
- *"Research AI trends, write summary, generate infographic"*

### 🎯 Multi-Agent Coordination (Automatic)
```python
from core import A2AClient

client = A2AClient()

# Complex request → Automatic agent coordination
result = await client.send_message(
    agent_url="http://localhost:8000",
    user_input="Research renewable energy trends and create article with solar panel image"
)

# Results: 25+ sources researched → 900+ word article → 1MB+ image generated
print(f"Tasks executed: {result['tasks_completed']}")
print(f"Research sources: {result['research_sources']}")  
print(f"Article length: {result['word_count']} words")
print(f"Image saved: {result['image_path']}")
```

### 🔍 Individual Agent Testing
```python
# Research Agent - Web search & data collection
result = await client.send_message(
    "http://localhost:8003",
    "Research latest developments in AI agents"
)
# Returns: 25 sources, summaries, structured data

# Writing Agent - Context-aware content creation  
result = await client.send_message(
    "http://localhost:8002",
    "Write comprehensive article about Model Context Protocol"
)
# Returns: 1200+ word article with title and structure

# Image Agent - Professional visuals
result = await client.send_message(
    "http://localhost:8001",
    "Create professional diagram of multi-agent AI system"
)
# Returns: High-quality image saved to generated_images/
```

### 🧪 Testing & Debugging
```bash
# Test all agent coordination
uv run python test_coordination.py

# Test individual agents
uv run python test_individual_agents.py
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

## ✅ System Status

### 🎉 Fully Operational (v2.0)
- ✅ **Multi-Agent Coordination**: Sequential workflows with context passing
- ✅ **Intent Detection**: LLM-based request analysis and agent routing  
- ✅ **Real Data Processing**: 25+ sources, 900+ word articles, 1MB+ images
- ✅ **File-based Workflows**: Organized result storage with metadata
- ✅ **Error Handling**: Graceful failure handling and comprehensive logging
- ✅ **Testing Suite**: Complete testing infrastructure for all components

### 🔮 Future Enhancements
1. **Authentication**: Implement agent-to-agent security tokens
2. **Persistence**: Add database storage for task history
3. **Monitoring**: Real-time metrics and performance dashboards  
4. **API Documentation**: OpenAPI/Swagger documentation
5. **Docker**: Containerization for production deployment
6. **Load Balancing**: Multiple agent instances for scalability

## 👨‍💻 Author

**Dr. Wai Yan Nyein Naing**
- GitHub: [@WaiYanNyeinNaing](https://github.com/WaiYanNyeinNaing)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.