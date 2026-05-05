"""
Streamlit web UI for Tool-Using Agent (Week 1)
Connects to Ollama or Groq for LLM inference.

Set OLLAMA_BASE_URL orGROQ_API_KEY in Streamlit Cloud secrets.
"""

import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# ── LLM Config ────────────────────────────────────────────────────────────────

def get_model():
    """Connect to Ollama or Groq based on available secrets."""
    groq_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

    if groq_key:
        from langchain_groq import ChatGroq
        return ChatGroq(model="llama-3.3-70b-versatile", api_key=groq_key)

    # Fall back to local Ollama
    from langchain_ollama import ChatOllama
    base = os.getenv("OLLAMA_BASE_URL") or st.secrets.get("OLLAMA_BASE_URL", "http://localhost:11434")
    return ChatOllama(model="qwen3.5:9b", base_url=base, temperature=0.3)


def build_agent(model):
    from langgraph.prebuilt import create_react_agent

    from langchain_core.tools import tool
    import re
    from ddgs import DDGS

    @tool
    def web_search(query: str) -> str:
        """Search the web using DuckDuckGo."""
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found."
        return "\n".join(
            f"- {r['title']}: {r['body']} (URL: {r['href']})"
            for r in results
        )

    @tool
    def calculator(expression: str) -> str:
        """Evaluate a mathematical expression. Only handles safe arithmetic."""
        safe = re.sub(r"[^0-9+\-*/.()% ]", "", expression)
        try:
            result = eval(safe, {"__builtins__": {}}, {})
            return f"{expression} = {result}"
        except Exception as e:
            return f"Error: {e}"

    @tool
    def file_read(path: str) -> str:
        """Read the contents of a text file. Returns full content or an error."""
        try:
            with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 5000:
                content = content[:5000] + f"\n\n[... Truncated at 5000 chars ...]"
            return content
        except Exception as e:
            return f"Error reading {path}: {e}"

    tools = [web_search, calculator, file_read]
    return create_react_agent(model, tools), tools


# ── Streamlit UI ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Tool-Using Agent", page_icon="🤖")
st.title("🤖 Tool-Using Agent")
st.markdown("**Week 1** — ReAct loop with LangGraph. Try asking something!")

# Session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "streamlit-default"
if "agent" not in st.session_state:
    st.session_state.agent = None
if "tools" not in st.session_state:
    st.session_state.tools = None
if "history" not in st.session_state:
    st.session_state.history = []

# Init agent on first run
if st.session_state.agent is None:
    try:
        model = get_model()
        st.session_state.agent, st.session_state.tools = build_agent(model)
        st.success(f"Agent ready. Tools: {[t.name for t in st.session_state.tools]}")
    except Exception as e:
        st.error(f"Failed to connect to LLM: {e}")
        st.info("Set `GROQ_API_KEY` or `OLLAMA_BASE_URL` in Streamlit secrets.")

# Thread selector
thread_id = st.text_input("Thread ID", value=st.session_state.thread_id)
if thread_id != st.session_state.thread_id:
    st.session_state.thread_id = thread_id
    st.session_state.history = []  # reset history on thread change
    st.rerun()

# Chat history display
for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config={"configurable": {"thread_id": st.session_state.thread_id}},
                )
                answer = response["messages"][-1].content
                st.markdown(answer)
                st.session_state.history.append({"role": "assistant", "content": answer})
            except Exception as e:
                err = f"Error: {e}"
                st.error(err)
                st.session_state.history.append({"role": "assistant", "content": err})

# Clear history button
if st.button("🗑️ Clear thread history"):
    st.session_state.history = []
    st.rerun()
