# Tool-Using Agent

A ReAct loop agent built with LangGraph that reasons about user queries, calls tools, and returns responses. Demonstrates the core pattern for building tool-augmented LLMs — the foundation of agentic AI systems.

**[→ Deploy to Streamlit Cloud](https://streamlit.io/cloud)**

## What This Project Demonstrates

- **ReAct pattern** (Reason + Act): The agent thinks step-by-step, decides when to call tools, observes results, and responds — the same loop behind production agents like LangChain's agent executors.
- **LangGraph `create_react_agent`**: How to use LangGraph's prebuilt ReAct agent factory instead of building the state machine from scratch — useful until you need custom control flow.
- **Tool abstraction with `@tool` decorators**: How to define tools that the LLM can invoke, with docstrings that double as prompts the model reads.
- **Multi-tool orchestration**: Three real tools (web search, calculator, file read) that show how to compose different tool types in one agent.

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | LangGraph 1.x | Checkpointing, streaming, production-tested |
| LLM | Ollama qwen3.5:9b | Local, free, fast on M1/M2 |
| Tools | DuckDuckGo, eval, file I/O | Real utilities, no mocks |

## Tools

| Tool | What it does |
|------|-------------|
| `web_search` | Searches DuckDuckGo, returns top 5 results with titles and URLs |
| `calculator` | Safe arithmetic — strips all non-math characters before evaluating |
| `file_read` | Reads any text file from disk, truncates at 5000 chars |

## Run Locally

```bash
cd ~/Work/revidev/portofolio/01-foundation/tool-use-agent
source .venv/bin/activate
python agent.py          # CLI
streamlit run streamlit_app.py  # Web UI
```

## Deploy to Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Connect this GitHub repo
3. Deploy — gets you a live URL in ~2 minutes

**Secrets (optional):**
- `GROQ_API_KEY` — use Groq instead of local Ollama
- `OLLAMA_BASE_URL` — point to a remote Ollama instance

## Architecture

```
User query
    ↓
create_react_agent (LangGraph)
    ↓
LLM decides: respond directly OR call a tool
    ↓
ToolNode executes → result → LLM
    ↓
Final response
```

The agent loop:
1. LLM sees the conversation history
2. LLM decides to call a tool or respond
3. If tool call → `ToolNode` executes it, result goes back to LLM
4. Repeat until LLM responds directly

## Key Decisions

1. **`create_react_agent` over manual graph** — less code, LangGraph handles the loop. You graduate to manual graph building when you need custom control flow (e.g., looping until a condition is met).
2. **`@tool` decorator with docstrings** — the docstring is part of the tool definition. The LLM reads it to decide when to call the tool. Write it like a instruction, not a description.
3. **`eval` with sanitization** — the calculator strips everything except digits and `+-*/.()% ` before calling `eval()`. No `exec`, no `__import__`, no access to Python builtins.

## Project Structure

```
.
├── agent.py           # Agent factory + CLI entry point
├── streamlit_app.py   # Web UI
├── memory.py          # (Week 2) ChromaDB-backed conversation memory
├── requirements.txt   # Python dependencies
└── README.md
```

## Extending

This is the base agent. To add capabilities:
- **Memory**: See the [memory-agent](../memory-agent/) project
- **Planning**: Add task decomposition — break a complex query into steps
- **RAG**: Add a knowledge base — ground responses in documents

## Test

```bash
source .venv/bin/activate
python3 -c "
from langchain_core.messages import HumanMessage
from agent import build_agent

agent, tools = build_agent()
result = agent.invoke(
    {'messages': [HumanMessage(content='What is 15 * 23?')]},
    config={'configurable': {'thread_id': 'test'}}
)
print(result['messages'][-1].content)
"
```
