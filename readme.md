# 🏗️ Architecture

The system follows a multi-agent workflow where each agent handles a specific responsibility in the diagram generation pipeline.

```
                    User
                     |
                     v
            Diagram Supervisor
                     |
                     v
              Concept Agent
                     |
                     v
            Components Agent
                     |
            +--------+--------+
            |                 |
            v                 v
      Layout Agent     Design Agent
            |                 |
            +--------+--------+
                     |
                     v
            Excalidraw Agent
                     |
            +--------+--------+
            |                 |
            v                 v
        Create View        Export
```

### Agent Responsibilities

| Agent | Responsibility |
|-------|---------------|
| **Supervisor** | Orchestrates the workflow and routes between agents |
| **Concept Agent** | Determines topic, entities, relationships, and groups from user query |
| **Components Agent** | Identifies nodes (id, label) and connections between nodes based on concept |
| **Layout Agent** | Determines diagram flow and calculates x, y positions for nodes |
| **Design Agent** | Assigns shapes (rectangle, circle, diamond, etc.) and fill styles to nodes |
| **Excalidraw Agent** | Assembles everything into a valid Excalidraw elements array |

---

# 📁 Repository Hierarchy

```
Excalidraw-mcp-AI-Agent/
│
├── excalidraw_agent/
│   ├── chat.py                 # CLI interface
│   ├── state.py                # DiagramState definitions
│   ├── graph.py                # LangGraph workflow
│   ├── main.py                 # Entry point
│   │
│   ├── services/
│   │   └── llm.py              # LLM service wrapper
│   │
│   ├── agents/
│   │   ├── supervisor.py       # Orchestrator agent
│   │   ├── concept.py          # Concept extraction
│   │   ├── components.py       # Component identification
│   │   ├── layout.py           # Layout calculation
│   │   ├── design.py           # Design & styling
│   │   └── excalidraw.py       # Excalidraw generation
│   │
│   ├── mcp/
│   │   └── excalidraw_client.py # MCP client for Excalidraw
│   │
│   └── prompts/
│       ├── concept.py          # Concept agent prompts
│       ├── layout.py           # Layout agent prompts
│       ├── components.py       # Components agent prompts
│       ├── design.py           # Design agent prompts
│       └── excalidraw.py       # (deprecated)
│
├── excalidraw-mcp/             # Excalidraw MCP server submodule
├── README.md
└── requirements.txt
```

---

# 🚀 Setup Instructions

## 1. Clone the Repository

```bash
git clone <repo-url>
cd Excalidraw-mcp-AI-Agent
```

## 2. Set Up Excalidraw MCP Server

```bash
cd excalidraw-mcp
git clone https://github.com/excalidraw/excalidraw-mcp.git .
pnpm install && pnpm run build
```

## 3. Python Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

# 💻 Simple MCP Client Example

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

async def main():
    # Start Excalidraw MCP server
    server_params = StdioServerParameters(
        command="node",
        args=[
            "/Users/me/projects/excalidraw-mcp-app/dist/index.js",
            "--stdio"
        ],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Get Excalidraw tools
            tools = await load_mcp_tools(session)
            
            print("Available tools:")
            for t in tools:
                print(f"  - {t.name}")

asyncio.run(main())
```

---

# 🎯 Usage Example

**Input:**
```
draw a diagram explaining Retrieval Augmented Generation (RAG)
```

**CLI Output:**
![CLI Output](./assets/Capture%20d'écran%202026-07-26%20103314.png)

**Generated Diagram:**
![RAG Diagram](./assets/Capture%20d'écran%202026-07-26%20103653.png)

The agent returns an Excalidraw URL where you can visualize and interact with your diagram.

---

# 📋 Excalidraw Element Schema

### Required Fields (All Elements)
- `type`: Element type (rectangle, ellipse, diamond, arrow, text)
- `id`: Unique identifier
- `x`: X-coordinate position
- `y`: Y-coordinate position

### Shape Elements (Rectangle/Ellipse/Diamond)
```json
{
  "type": "rectangle",
  "id": "node_1",
  "x": 100,
  "y": 200,
  "width": 200,
  "height": 100,
  "backgroundColor": "#4a90e2",
  "fillStyle": "solid",
  "strokeColor": "#2c3e50",
  "strokeWidth": 2,
  "roundness": {"type": 3},
  "boundElements": [{"id": "text_1", "type": "text"}]
}
```

### Text Elements (Inside Nodes)
```json
{
  "type": "text",
  "id": "text_1",
  "containerId": "node_1",
  "x": 120,
  "y": 235,
  "text": "Node Label",
  "textAlign": "center",
  "verticalAlign": "middle",
  "fontSize": 16,
  "fontFamily": 1
}
```
- Position text centered within parent: `x = parent.x + 20`, `y = parent.y + parent.height/2 - 15`
- Width should be `parent.width - 40`

### Arrow Elements
```json
{
  "type": "arrow",
  "id": "arrow_1",
  "x": 200,
  "y": 250,
  "points": [[0, 0], [100, 0]],
  "strokeColor": "#2c3e50",
  "strokeWidth": 2,
  "startBinding": {
    "elementId": "node_1",
    "focus": 0,
    "gap": 5
  },
  "endBinding": {
    "elementId": "node_2",
    "focus": 0.2,
    "gap": 5
  }
}
```
- For bidirectional arrows, use `focus` offset (e.g., -0.2 and 0.2) to prevent overlap

### Text Labels (Standalone)
```json
{
  "type": "text",
  "id": "label_1",
  "x": 400,
  "y": 300,
  "text": "Standalone Text",
  "fontSize": 14,
  "fontFamily": 1,
  "textAlign": "center"
}
```

### Styling Rules
- `fillStyle`: `"solid"` for colored nodes, `"transparent"` for frames
- IDs must be unique across ALL elements

---

# 📝 Development Roadmap

- [x] Create all agents (Supervisor, Concept, Components, Layout, Design, Excalidraw)
- [ ] Add agent-level unit tests
- [ ] Add chat history file logging
- [ ] Implement caching for LLM responses
- [ ] Supervisor intent detection with routing
- [ ] Human-in-the-loop interaction
- [ ] Checkpointing for diagram modification
- [ ] Comprehensive logging system

---

# 🔧 Architecture Changes

The system now features a refined agent pipeline:

1. **Supervisor Agent** → Orchestrates the entire workflow
2. **Concept Agent** → Analyzes query and extracts key concepts
3. **Components Agent** → Identifies nodes and relationships
4. **Parallel Processing**:
   - **Layout Agent** → Determines flow and positions
   - **Design Agent** → Assigns shapes and styles
5. **Excalidraw Agent** → Assembles final diagram elements
