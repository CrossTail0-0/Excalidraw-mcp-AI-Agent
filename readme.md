# 🏗️ Architecture

The system follows a multi-agent workflow with Redis caching for fast diagram retrieval.

```
                    User
                     |
                     v
              Intent Detector
                     |
            +--------+--------+
            |                 |
            v                 v
      Diagram Request    General Question
            |                 |
            v                 v
    +-------+-------+    Direct Responder
    |               |         |
    v               v         v
Check Redis    Diagram    (Return Response)
    Cache      Supervisor
    |               |
    |               v
    |        Concept Agent
    |               |
    |               v
    |       Components Agent
    |               |
    |       +-------+-------+
    |       |               |
    |       v               v
    |   Layout Agent    Design Agent
    |       |               |
    |       +-------+-------+
    |               |
    |               v
    |       Excalidraw Agent
    |               |
    |       +-------+-------+
    |       |               |
    |       v               v
    |   Create View       Export
    |       |               |
    |       +-------+-------+
    |               |
    |               v
    |       Save to Redis
    |               |
    +-------+-------+
            |
            v
        Response
```

### Cache Flow Explanation

1. **Intent Detector** → Determines if user wants a diagram
2. **Check Redis Cache** → For diagram requests, check if the exact query is cached
   - **Cache HIT** → Skip all agents, directly return cached diagram
   - **Cache MISS** → Continue through the full diagram pipeline
3. **Diagram Pipeline** → Full agent workflow to generate new diagram
4. **Save to Redis** → After successful generation, store the result in Redis cache
5. **Response** → Return the diagram (cached or newly generated)

### Agent Responsibilities

| Agent | Responsibility |
|-------|---------------|
| **Intent Detector** | Determines if user wants a diagram or is asking a general question |
| **Redis Cache** | Checks for cached diagrams and stores new ones (30-day TTL) |
| **Direct Responder** | Handles non-diagram queries with conversational responses |
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
│   ├── chat.py                 # CLI interface with intent handling
│   ├── state.py                # DiagramState definitions
│   ├── graph.py                # LangGraph workflow with Redis caching
│   ├── main.py                 # Entry point
│   │
│   ├── services/
│   │   └── llm.py              # LLM service wrapper (Groq)
│   │
│   ├── agents/
│   │   ├── intent.py           # Intent detection agent
│   │   ├── responder.py        # Direct response agent for general queries
│   │   ├── supervisor.py       # Orchestrator agent
│   │   ├── concept.py          # Concept extraction
│   │   ├── components.py       # Component identification
│   │   ├── layout.py           # Layout calculation
│   │   ├── design.py           # Design & styling
│   │   └── excalidraw.py       # Excalidraw generation
│   │
│   ├── cache/
│   │   ├── __init__.py
│   │   └── diagram_cache.py    # Redis-based caching
│   │
│   ├── history/
│   │   ├── __init__.py
│   │   └── storage.py          # Chat history storage
│   │
│   ├── mcp/
│   │   └── excalidraw_client.py # MCP client for Excalidraw
│   │
│   └── prompts/
│       ├── intent.py
│       ├── responder.py
│       ├── concept.py          # Concept agent prompts
│       ├── layout.py           # Layout agent prompts
│       ├── components.py       # Components agent prompts
│       ├── design.py           # Design agent prompts
│       └── excalidraw.py       # (deprecated)
│
├── excalidraw-mcp/             # Excalidraw MCP server submodule
├── CHAT_HISTORY/               # Chat history storage
├── DIAGRAM_CACHE/              # SQLite cache fallback
├── docker-compose.yml          # Redis Docker setup
├── README.md
├── requirements.txt
└── .env
```

---

# 🚀 Setup Instructions

## 1. Clone the Repository

```bash
git clone <repo-url>
cd Excalidraw-mcp-AI-Agent
```

## 2. Start Redis with Docker (Optional)

```bash
# Using Docker Compose
docker compose up -d

# Or with Docker run
docker run -d --name excalidraw-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  redis:alpine redis-server --appendonly yes
```

## 3. Set Up Excalidraw MCP Server

```bash
cd excalidraw-mcp
git clone https://github.com/excalidraw/excalidraw-mcp.git .
pnpm install && pnpm run build
```

## 4. Python Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 5. Environment Variables

Create a `.env` file in the root directory:

```env
# LLM
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.1-8b-instant

# Redis Cache (Optional - falls back to SQLite if not set)
REDIS_URL=redis://localhost:6379/0
REDIS_TTL=2592000  # 30 days in seconds

# Excalidraw MCP Server Configuration
EXCALIDRAW_MCP_PATH=path/to/excalidraw-mcp/dist/index.js
EXCALIDRAW_MCP_COMMAND=node
EXCALIDRAW_MCP_TRANSPORT=--stdio
```

---

# 💻 Docker Compose File

`docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    container_name: excalidraw-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped

volumes:
  redis_data:
```

---

# 🎯 Usage Examples

## First Request (Cache MISS)

**Input:**
```
draw a diagram explaining Retrieval Augmented Generation (RAG)
```

**CLI Output:**
```
⏳ Processing... (Message #1)
🔍 Checking Redis cache...
❌ Cache MISS. Generating new diagram...

📐 DIAGRAM GENERATED
============================================================
🆕 NEWLY GENERATED
📝 Topic: Retrieval Augmented Generation (RAG)
🔹 Entities: Query, Retriever, Knowledge Base, LLM, Response
🔸 Relationships: 4 identified
🟦 Nodes: 5
🔗 Connections: 8
📊 Flow: Sequential with retrieval
🎨 Shapes: 5 assigned
📦 Total Elements: 23
------------------------------------------------------------
🔗 VIEW YOUR DIAGRAM:
   https://excalidraw.com/room#xyz789
============================================================
💾 Saving to Redis cache...
✅ Cached successfully in Redis!
💾 Auto-saved to: CHAT_HISTORY/chat_history_20260115_143000.json
```

**Excalidraw Diagram**
![](./assets/Capture%20d'écran%202026-07-26%20104639.png)

## Same Request Again (Cache HIT)

**Input:**
```
draw a diagram explaining Retrieval Augmented Generation (RAG)
```

**CLI Output:**
```
⏳ Processing... (Message #2)
🔍 Checking Redis cache...
✅ Cache HIT! Returning cached diagram.

📐 DIAGRAM GENERATED
============================================================
⚡ FROM REDIS CACHE (Fast retrieval)
📌 Original query: draw a diagram explaining Retrieval Augmented Generation (RAG)
📝 Topic: Retrieval Augmented Generation (RAG)
🟦 Nodes: 5
🔗 Connections: 8
📦 Total Elements: 23
------------------------------------------------------------
🔗 VIEW YOUR DIAGRAM:
   https://excalidraw.com/room#xyz789
============================================================
💾 Auto-saved to: CHAT_HISTORY/chat_history_20260115_144500.json
```

## General Question (No Cache)

**Input:**
```
What is Retrieval Augmented Generation?
```

**CLI Output:**
```
⏳ Processing... (Message #3)
🤖 Assistant:
============================================================
Retrieval Augmented Generation (RAG) is an AI framework that 
combines information retrieval with language generation. 

Key components:
1. **Retriever**: Searches for relevant information from a knowledge base
2. **Generator**: Uses retrieved context to generate accurate responses

RAG improves accuracy by grounding LLM responses in external 
knowledge sources, reducing hallucinations and enabling access 
to up-to-date information.

💡 Tip: I can draw a diagram of the RAG architecture if you'd like!
============================================================
💾 Auto-saved to: CHAT_HISTORY/chat_history_20260115_145000.json
```

---

# 🔄 Graph Flow with Redis Cache

The graph includes intelligent caching for diagram requests:

```python
# Conditional routing with cache
async def check_cache(state):
    """Check Redis cache before generating."""
    cached = await cache.get_cached_result(state["user_query"])
    if cached:
        state["elements"] = cached["elements"]
        state["export_url"] = cached["export_url"]
        state["is_cached"] = True
    return state

def route_after_cache(state):
    if state.get("is_cached", False):
        return "render_directly"  # Skip all agents
    return "generate_diagram"     # Full pipeline
```

### Cache Flow Diagram

```
+------------------+
|   User Request   |
+------------------+
         |
         v
+------------------+
|  Intent Detector |
+------------------+
         |
    +----+----+
    |         |
    v         v
+---------+ +------------------+
| Diagram | | General Question |
| Request | +------------------+
+---------+          |
    |                v
    v         +-------------+
+-----------+ | Direct      |
| Check     | | Responder   |
| Redis     | +-------------+
| Cache     |       |
+-----------+       v
    |        +-------------+
    |        |   Response  |
+---+---+    +-------------+
|   |   |
v   v   v
+-----------+  +----------------+
| Cache HIT |  | Cache MISS     |
| (Skip     |  | (Full Pipeline)|
| Pipeline) |  +----------------+
+-----------+          |
    |                 v
    |         +---------------+
    |         | Diagram       |
    |         | Supervisor    |
    |         +---------------+
    |                 |
    |                 v
    |         +---------------+
    |         | Concept Agent |
    |         +---------------+
    |                 |
    |                 v
    |         +---------------+
    |         | Components    |
    |         | Agent         |
    |         +---------------+
    |                 |
    |         +-------+-------+
    |         |               |
    |         v               v
    |   +---------+     +---------+
    |   | Layout  |     | Design  |
    |   | Agent   |     | Agent   |
    |   +---------+     +---------+
    |         |               |
    |         +-------+-------+
    |                 |
    |                 v
    |         +---------------+
    |         | Excalidraw    |
    |         | Agent         |
    |         +---------------+
    |                 |
    |         +-------+-------+
    |         |               |
    |         v               v
    |   +---------+     +---------+
    |   | Create  |     | Export  |
    |   | View    |     |         |
    |   +---------+     +---------+
    |         |               |
    |         +-------+-------+
    |                 |
    |                 v
    |         +---------------+
    |         | Save to       |
    |         | Redis Cache   |
    |         +---------------+
    |                 |
    +-------+---------+
            |
            v
    +-------------+
    |   Response  |
    | (with URL)  |
    +-------------+
```

---

# 💾 Redis Cache Implementation

## Cache Features

- **Automatic TTL**: 30-day expiration
- **Fallback**: SQLite cache if Redis is unavailable
- **Async Support**: Non-blocking operations
- **Connection Pooling**: Efficient Redis connections
- **Key Management**: SHA256 hashing for query keys

## Cache Statistics

```python
# View cache stats
await cache.get_stats()
```

Output:
```json
{
  "total_entries": 15,
  "cache_type": "Redis",
  "redis_url": "redis://localhost:6379/0",
  "fallback_to_memory": true,
  "ttl_seconds": 2592000,
  "ttl_days": 30,
  "status": "connected"
}
```

---

# 📋 Development Roadmap

- [x] Create all agents (Intent, Responder, Supervisor, Concept, Components, Layout, Design, Excalidraw)
- [x] Implement Redis caching
- [x] Add SQLite fallback
- [x] Add chat history storage
- [ ] Add agent-level unit tests
- [ ] Human-in-the-loop interaction
- [ ] Checkpointing for diagram modification
- [ ] Comprehensive logging system

---

# 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
