from typing import List, Dict, Any, Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[Dict[str, str]], add_messages]
    retrieved_docs: Optional[List[str]]
    tool_results: Optional[Dict[str, Any]]
    current_step: Optional[str]