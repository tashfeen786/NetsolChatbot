import logging
import time
from langchain_core.messages import BaseMessage
from ..state import AgentState

logger = logging.getLogger(__name__)

def _get_last_user_message(messages):
    for msg in reversed(messages):
        if isinstance(msg, dict):
            if msg.get("role") == "user":
                return msg.get("content", "")
        elif isinstance(msg, BaseMessage):
            if msg.type == "human":
                return msg.content
    return None

def retriever_node(state: AgentState) -> AgentState:
    print("🔍 Entering retriever_node")
    messages = state.get("messages", [])
    if not messages:
        return {"retrieved_docs": []}

    query = _get_last_user_message(messages)
    if not query:
        return {"retrieved_docs": []}
    print(f"🔍 Query: {query[:50]}...")

    try:
        from ..rag.vector_store import get_vector_store
        print("🔍 Getting vector store...")
        vector_store = get_vector_store()
        print("🔍 Performing similarity search...")
        start = time.time()
        docs = vector_store.similarity_search(query, k=10)
        print(f"🔍 Search completed in {time.time()-start:.2f}s")
        retrieved = [doc.page_content for doc in docs]
        print(f"🔍 Retrieved {len(retrieved)} docs")
        return {"retrieved_docs": retrieved}
    except Exception as e:
        import traceback
        print(f"❌ Retriever error: {e}")
        traceback.print_exc()
        return {"retrieved_docs": []}