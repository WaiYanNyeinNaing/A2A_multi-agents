# 🔍 Testing Research Capabilities

## 🚀 Quick Start Guide

### 1. Start the Research Agents

Open **5 terminals** and run:

```bash
# Terminal 1: Assistant (Orchestrator)
uv run python servers/assistant_server.py

# Terminal 2: Writing Agent
uv run python servers/writing_server.py

# Terminal 3: Image Agent  
uv run python servers/image_server.py

# Terminal 4: Research Agent (NEW!)
uv run python servers/research_server.py

# Terminal 5: Report Agent (NEW!)
uv run python servers/report_server.py
```

### 2. Launch Interactive Interface

```bash
# Terminal 6: Interactive Interface
uv run python tools/interactive_interface.py
```

## 🧪 Test Scenarios

### 📋 Scenario 1: Direct Research Agent Testing

1. Choose option `4` (Research Specialist)
2. Try these prompts:

**Basic Web Search:**
```
Latest developments in artificial intelligence 2024
```

**Topic Research:**
```
Climate change impact on agriculture
```

**Fact Checking:**
```
Electric vehicles produce zero emissions
```

### 📊 Scenario 2: Direct Report Agent Testing

1. Choose option `5` (Report Writing Specialist)
2. Try these prompts:

**Research Report (you need to provide research data):**
```
Create a comprehensive report on AI trends. Research data: [AI is transforming industries, machine learning advances, GPT models improving, ethical concerns rising, investment increasing 40% in 2024]
```

**Executive Summary:**
```
Generate an executive summary from this research: [paste research findings here]
```

### 🎯 Scenario 3: Coordinated Research Workflow

1. Choose option `1` (Assistant Agent - Orchestrator)
2. Try this complex prompt:

```
Research the latest trends in renewable energy and create a comprehensive report with an image of solar panels
```

**What should happen:**
- Assistant coordinates with Research Agent to gather data
- Assistant coordinates with Report Agent to create report
- Assistant coordinates with Image Agent for visuals
- You get a complete research report with images

### 🔧 Scenario 4: Step-by-Step Workflow

**Step 1: Research**
- Use Research Agent: `"Research renewable energy trends 2024"`
- Save the results

**Step 2: Report Writing**  
- Use Report Agent: `"Create comprehensive report on: [paste research from step 1]"`
- Save the report

**Step 3: Visual Enhancement**
- Use Image Agent: `"Generate solar panel installation image"`
- Save the image

## 📝 Expected Outputs

### 🔍 Research Agent Results:
- **Web Search**: List of search results with titles, links, snippets
- **Topic Research**: Comprehensive research summary with multiple sources
- **Fact Check**: Analysis of claim with credible sources

### 📊 Report Agent Results:
- **Research Report**: Structured markdown report (2000+ words)
- **Executive Summary**: Concise summary (300 words)
- **HTML Report**: Professional HTML document
- **Slide Outline**: Presentation structure

### 🎯 Assistant Coordination:
- **Multi-agent**: Combines research + report + images
- **Structured**: Well-organized final output
- **Complete**: All aspects covered in one response

## 🐛 Troubleshooting

**"Research Agent not ready"**
- Check SERPER_API_KEY in .env file
- Make sure research server is running on port 8003

**"No search results"**
- Verify SERPER_API_KEY is valid
- Check internet connection
- Try simpler search terms

**"Agent offline"**
- Ensure all 5 agent servers are running
- Check ports: 8000, 8001, 8002, 8003, 8004
- Wait a moment for agents to fully initialize

**"Report generation failed"**
- Make sure GEMINI_API_KEY is configured
- Provide adequate research data for report generation
- Try shorter, simpler prompts first

## 💡 Pro Tips

1. **Start Simple**: Test each agent individually before trying coordination
2. **Save Results**: Use custom names to organize your research outputs
3. **Chain Workflows**: Use output from one agent as input to another
4. **Check Status**: Use option 6 to verify all agents are online
5. **Be Patient**: Research and report generation can take 30-60 seconds

## 🎉 Success Indicators

✅ All 5 agents show "Online" in status check  
✅ Research returns real web search results  
✅ Reports are generated in markdown format  
✅ Files are saved to `my_results/` directory  
✅ Assistant can coordinate multiple agents  

Happy researching! 🚀