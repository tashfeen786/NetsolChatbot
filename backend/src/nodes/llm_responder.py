import logging
import time
from datetime import datetime  # ⬅️ NEW: Current date ke liye
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

    # 🔥 FIX: Current date, time, aur year extract 
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")        # e.g., 2026-06-24
    current_time_str = now.strftime("%H:%M")    # e.g., 14:30
    current_year = now.year                     # e.g., 2026

    system_content = (
    f"You are a helpful assistant for NetsolTech.\n\n"
    f"CURRENT DATE & TIME: Today is {today_str}. Current time is {current_time_str} (Asia/Karachi).\n"
    f"The current year is {current_year}.\n\n"
    
    "PRIMARY BEHAVIOR:\n"
    "- You have a knowledge base (provided as Context below). "
    "ALWAYS read and use this context to answer questions. "
    "If the context contains relevant information, answer from it directly.\n\n"
    
    "TOOLS:\n"
    "- `retrieve`: 🔥 **MANDATORY** for ANY question about uploaded files (PDF, DOCX, TXT). "
    "This tool searches ACROSS ALL UPLOADED FILES automatically. "
    "You do NOT need to specify a filename — the system will find the most relevant chunks "
    "from whichever file(s) match the user's question. "
    "If the user asks about 'PyTorch', it will automatically find PyTorch-related content. "
    "If they ask about 'Netsol', it will find Netsol content. "
    "If they ask a general question, it may pull from multiple files if relevant.\n"
    "- `get_upcoming_events`: meetings, schedule, calendar queries.\n"
    "- `create_calendar_event`: schedule new meetings.\n"
    "  ⚠️ IMPORTANT: You must provide `start_time` and `end_time` in ISO format with timezone offset +05:00.\n"
    "  DO NOT ask user for timezone — assume Asia/Karachi.\n"
    "- `web_search`: current news, weather, prices.\n"
    "- `query_business_database`: ANY question about sales, revenue, orders, "
    "customers, products, invoices, finance data — ALWAYS call this tool.\n\n"
    
    "📅 CALENDAR DATE PARSING RULES:\n"
    f"1. If user says 'tomorrow', calculate date as {today_str} + 1 day.\n"
    f"2. If user says 'June 25' (without year), assume the current year ({current_year}).\n"
    f"3. For `create_calendar_event`, the `start_time` and `end_time` MUST be in "
    "ISO 8601 format WITH timezone offset: YYYY-MM-DDTHH:MM:SS+05:00 (e.g., 2026-06-25T14:00:00+05:00).\n"
    "   ALWAYS append '+05:00' to the end (because we are in Asia/Karachi timezone).\n"
    "   DO NOT ask the user about timezone — assume Asia/Karachi (+05:00) by default.\n"
    "4. If user says 'for 1 hour', add 1 hour to start time to calculate end_time, "
    "   and also keep the +05:00 offset.\n"
    "5. Example: User asks 'meeting tomorrow at 10am' → start_time = '2026-06-25T10:00:00+05:00', "
    "   end_time = '2026-06-25T11:00:00+05:00' (if duration not given, assume 1 hour).\n\n"
    
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
    "3. For uploaded files — ALWAYS call `retrieve`. Let the system handle which file to read.\n"
    "4. Never guess business figures or file content.\n"
    "5. When the user says 'the uploaded file' without naming it, just call `retrieve` with their question — the system will fetch the best match across all files.\n"
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