# Tool-Using Agent — Week 1 Foundation

ReAct loop agent built with LangGraph + Ollama (qwen3.5:9b). The foundation that all other agents extend.

**[→ Deploy to Streamlit Cloud](https://streamlit.io/cloud)** — connect repo, deploy main branch, done in 2 min.

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | LangGraph 1.x | Production-grade, checkpointing, ReAct built-in |
| LLM | Ollama qwen3.5:9b | 100% local, private, free |
| Tools | MCP-style custom `@tool` | Extensible, no MCP server needed yet |

## Tools

| Tool | What it does |
|------|-------------|
| `web_search` | DuckDuckGo search, returns top 5 results with URLs |
| `calculator` | Safe arithmetic evaluation |
| `file_read` | Read any text file from disk (truncates at 5000 chars) |

## Run Locally

```bash
cd ~/Work/revidev/portofolio/01-foundation/tool-use-agent
source .venv/bin/activate
python agent.py          # CLI mode
streamlit run streamlit_app.py  # Web UI
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub repo
4. Set secrets (optional):
   - `GROQ_API_KEY` — use Groq instead of local Ollama
   - `OLLAMA_BASE_URL` — custom Ollama endpoint

## Architecture

```
User query
    ↓
create_react_agent (LangGraph)
    ↓
LLM (qwen3.5:9b via Ollama)
    ↓
[Tool call?] → ToolNode → result → LLM → ...
    ↓
Final response
```

## Key Decisions

1. **Ollama over Groq** — local, private, no API rate limits. qwen3.5:9b is fast enough on CPU/M1.
2. **create_react_agent over manual graph** — less code, LangGraph handles the ReAct loop. Week 1 is about getting the pattern right, not optimizing.
3. **Custom `@tool` decorators** — not full MCP server yet. MCP comes in Week 5+ when tools need to be shared across agents.

## Extend

This agent is the base. Weeks 2–4 extend it:
- **Week 2:** Add memory (ChromaDB) — same tools, persistent conversations
- **Week 3:** Add planning (task decomposition) — same tools, visible reasoning steps
- **Week 4:** Add retrieval (RAG) — same tools, grounded in a knowledge base
