# Tool-Using Agent

## Stack
- LangGraph 1.x (create_react_agent)
- Ollama qwen3.5:9b at localhost:11434
- Python 3.13 + venv

## Run
```bash
source .venv/bin/activate
python agent.py          # CLI
streamlit run streamlit_app.py  # Web UI
```

## Key Files
- `agent.py` — ReAct loop agent with 3 tools (web_search, calculator, file_read)
- `streamlit_app.py` — Web UI
- `memory.py` — ChromaDB-backed conversation memory (see memory-agent project)
- `requirements.txt` — Python dependencies

## Tools
- `web_search` — DuckDuckGo via ddgs
- `calculator` — Safe arithmetic eval
- `file_read` — Read text files

## Test
```bash
source .venv/bin/activate
python3 -c "
from langchain_core.messages import HumanMessage
from agent import build_agent
agent, tools = build_agent()
result = agent.invoke({'messages': [HumanMessage(content='What is 15 * 23?')]}, config={'configurable': {'thread_id': 'test'}})
print(result['messages'][-1].content)
"
```
