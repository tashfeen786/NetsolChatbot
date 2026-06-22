import os, sqlite3, json, logging
from langchain_core.tools import tool

logger   = logging.getLogger(__name__)
DB_PATH  = os.getenv("BUSINESS_DB_PATH", "data/business.db")
_SCHEMA  = None

def _get_schema() -> str:
    global _SCHEMA
    if _SCHEMA:
        return _SCHEMA
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    parts = []
    for (table,) in cur.fetchall():
        cur.execute(f"PRAGMA table_info({table})")
        cols = ", ".join(f"{c[1]} {c[2]}" for c in cur.fetchall())
        parts.append(f"Table '{table}': {cols}")
    conn.close()
    _SCHEMA = "\n".join(parts)
    return _SCHEMA

def _run_sql(sql: str):
    sql = sql.strip().rstrip(";")
    if not sql.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur  = conn.cursor()
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchmany(50)]
    conn.close()
    return rows

@tool
def query_business_database(question: str) -> str:
    """Query the business SQLite database containing customers, products, orders,
    order_items, and invoices tables. Use this for ANY question about sales figures,
    revenue, orders, customers, products, invoices, or finance data.
    Returns structured data suitable for charts and tables."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    schema = _get_schema()
    llm    = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model=os.getenv("MODEL_NAME", "gemini-2.5-flash-lite"),
        temperature=0,
    )

    sql_prompt = f"""You are a SQLite expert. Write a single SELECT query for this question.
Schema:
{schema}

Rules: output ONLY raw SQL, no backticks, no explanation, no markdown.

Question: {question}
SQL:"""

    sql_raw = llm.invoke([HumanMessage(content=sql_prompt)]).content.strip()
    # Strip markdown fences if model adds them
    if "```" in sql_raw:
        sql_raw = "\n".join(
            l for l in sql_raw.splitlines() if not l.startswith("```")
        ).strip()

    print(f"📊 SQL: {sql_raw}")

    try:
        rows = _run_sql(sql_raw)
    except Exception as e:
        return f"SQL execution failed: {e}\nGenerated SQL: {sql_raw}"

    if not rows:
        return f"Query returned no results.\nSQL: {sql_raw}"

    # Tabular text for LLM context
    headers  = list(rows[0].keys())
    header_line = " | ".join(headers)
    divider     = "-" * len(header_line)
    data_lines  = [" | ".join(str(v) if v is not None else "NULL"
                              for v in r.values()) for r in rows]
    table_text  = "\n".join([header_line, divider] + data_lines)

    # Structured JSON for frontend chart rendering
    structured = json.dumps({
        "columns": headers,
        "rows":    rows,
        "count":   len(rows),
        "sql":     sql_raw,
    })

    print(f"📊 Returned {len(rows)} rows")
    return f"RESULTS ({len(rows)} rows):\n{table_text}\n\n<sql_result_json>{structured}</sql_result_json>"