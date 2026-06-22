from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from .state import AgentState
from .nodes.llm_responder import llm_responder
from .nodes.retriever import retriever_node
from .tools import TOOLS

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("retriever", retriever_node)
    builder.add_node("llm", llm_responder)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.set_entry_point("retriever")
    builder.add_edge("retriever", "llm")
    builder.add_conditional_edges(
        "llm",
        tools_condition,
        {"tools": "tools", END: END}
    )
    builder.add_edge("tools", "llm")

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    return graph