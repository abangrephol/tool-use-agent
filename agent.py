"""
Tool-Using Agent — ReAct Loop with LangGraph + Ollama

A reasoning + acting agent that decides when to call tools based on user queries.
Built with create_react_agent — the prebuilt LangGraph ReAct implementation.

Run:
  source .venv/bin/activate
  python agent.py
"""

import os
import re
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

# ─── TOOLS ───────────────────────────────────────────────────────────────────

def _make_tools():
    from ddgs import DDGS
    from langchain_core.tools import tool

    @tool
    def web_search(query: str) -> str:
        """Search the web using DuckDuckGo. Use for factual queries, current events, or anything requiring up-to-date information."""
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
        """Read the contents of a text file. Returns full content or an error message."""
        try:
            with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 5000:
                content = content[:5000] + f"\n\n[... Truncated at 5000 chars. Full: {len(content)} chars ...]"
            return content
        except Exception as e:
            return f"Error reading {path}: {e}"

    return [web_search, calculator, file_read]

# ─── AGENT FACTORY ───────────────────────────────────────────────────────────

def build_agent():
    model = ChatOllama(
        model="qwen3.5:9b",
        base_url="http://localhost:11434",
        temperature=0.3,
    )
    tools = _make_tools()
    # create_react_agent handles ReAct loop + tool routing automatically
    return create_react_agent(model, tools), tools

# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Tool-Using Agent — ReAct Loop")
    print("Model: Ollama qwen3.5:9b | Tools: web_search, calculator, file_read")
    print("Type 'exit' to quit")
    print("=" * 60)

    agent, tools = build_agent()
    print(f"Tools loaded: {[t.name for t in tools]}")

    thread_id = "default"

    while True:
        user = input("\nYou: ").strip()
        if user.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if not user:
            continue

        print("\nAgent thinking...")
        response = agent.invoke(
            {"messages": [HumanMessage(content=user)]},
            config={"configurable": {"thread_id": thread_id}},
        )

        # Print all AIMessage chunks (tool calls + final answer)
        for msg in response["messages"]:
            if isinstance(msg, HumanMessage):
                continue
            if hasattr(msg, "content") and msg.content:
                print(f"\nAgent: {msg.content}")

if __name__ == "__main__":
    main()
