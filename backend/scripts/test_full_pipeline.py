import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.nodes.llm_responder import llm_responder

def build_simple_graph():
    builder = StateGraph(AgentState)
    builder.add_node("llm", llm_responder)
    builder.set_entry_point("llm")
    builder.add_edge("llm", END)
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

def main():
    print("🔄 Building simple graph...")
    graph = build_simple_graph()
    thread_id = "test_thread_123"
    config = {"configurable": {"thread_id": thread_id}}
    input_state = {"messages": [{"role": "user", "content": "Who is the CEO of Netsol?"}]}
    
    print("🔄 Invoking simple graph...")
    result = graph.invoke(input_state, config)
    messages = result.get("messages", [])
    if messages:
        last = messages[-1]
        print(f"📄 Response: {last.get('content', 'N/A') if isinstance(last, dict) else last.content}")
    else:
        print("❌ No response")

if __name__ == "__main__":
    main()