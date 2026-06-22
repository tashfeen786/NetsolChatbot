import logging
import time
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from ..state import AgentState
from ..models.llm_factory import get_llm
from ..tools import TOOLS

logger = logging.getLogger(__name__)
llm = get_llm()
llm_with_tools = llm.bind_tools(TOOLS)

def _extract_message_data(msg):
    if isinstance(msg, dict):
        return msg.get("role", ""), msg.get("content", "")
    elif isinstance(msg, BaseMessage):
        if msg.type == "human":
            return "user", msg.content
        elif msg.type == "ai":
            return "assistant", msg.content
        elif msg.type == "system":
            return "system", msg.content
    return "", ""

def llm_responder(state: AgentState) -> AgentState:
    print("🤖 Entering llm_responder")
    messages = state.get("messages", [])
    retrieved_docs = state.get("retrieved_docs", [])
    print(f"🤖 Retrieved docs count: {len(retrieved_docs)}")

    system_content = (
    "You are a helpful assistant for NetsolTech.\n\n"
    "PRIMARY BEHAVIOR:\n"
    "- You have a knowledge base (provided as Context below). "
    "ALWAYS read and use this context to answer questions. "
    "If the context contains relevant information, answer from it directly.\n\n"
    "TOOLS:\n"
    "- `get_upcoming_events`: meetings, schedule, calendar queries.\n"
    "- `create_calendar_event`: schedule new meetings.\n"
    "- `web_search`: current news, weather, prices.\n"
    "- `query_business_database`: ANY question about sales, revenue, orders, "
    "customers, products, invoices, finance data — ALWAYS call this tool.\n\n"
    "VISUALIZATION RULES:\n"
    "When tool returns data with multiple rows suitable for a chart (comparisons, "
    "trends, distributions, rankings), include a <chart_data> JSON tag in your response.\n\n"
    "CRITICAL: xKey and yKey MUST exactly match the actual field names used inside "
    "each object in the data array. Do not invent generic names like 'name' or "
    "'value' — use the real column names from the query result.\n\n"
    "Example: if your data rows look like {\"status\": \"completed\", \"order_count\": 29}, "
    "then xKey must be \"status\" and yKey must be \"order_count\" — exactly matching "
    "the keys present in each data object. Every object in the data array must use "
    "the same two keys, consistently.\n\n"
    "Format:\n"
    "<chart_data>{\"type\":\"bar\",\"title\":\"Descriptive Title\","
    "\"xKey\":\"<actual_field_name_for_label>\",\"yKey\":\"<actual_field_name_for_value>\","
    "\"data\":[{\"<actual_field_name_for_label>\":\"...\",\"<actual_field_name_for_value>\":...}]}"
    "</chart_data>\n\n"
    "Concrete example with real data:\n"
    "<chart_data>{\"type\":\"pie\",\"title\":\"Order Status Distribution\","
    "\"xKey\":\"status\",\"yKey\":\"order_count\","
    "\"data\":[{\"status\":\"completed\",\"order_count\":29},"
    "{\"status\":\"cancelled\",\"order_count\":11},"
    "{\"status\":\"pending\",\"order_count\":10}]}</chart_data>\n\n"
    "- Use 'bar' for comparisons/rankings\n"
    "- Use 'line' for trends over time\n"
    "- Use 'pie' for distributions/percentages\n"
    "- Only include chart_data when it genuinely adds value.\n\n"
    "RULES:\n"
    "1. Context answer > tool call > saying you don't know.\n"
    "2. For business data — ALWAYS call `query_business_database`.\n"
    "3. Never guess business figures.\n"
)

    if retrieved_docs:
        context = "\n\n---\n\n".join(retrieved_docs)
        system_content += f"\n\nContext:\n{context}"
        print(f"🤖 Context length: {len(context)} chars")

    lc_messages = [SystemMessage(content=system_content)]
    for msg in messages:
        if isinstance(msg, BaseMessage) and msg.type in ("ai", "tool"):
            lc_messages.append(msg)
            continue
        role, content = _extract_message_data(msg)
        if not content:
            continue
        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))

    print("🤖 Calling LLM...")
    start = time.time()
    response = llm_with_tools.invoke(lc_messages)
    print(f"🤖 LLM responded in {time.time()-start:.2f}s")
    if getattr(response, "tool_calls", None):
        print(f"🤖 Tool calls requested: {[tc['name'] for tc in response.tool_calls]}")
    return {"messages": [response]}