import os
import requests
from langchain_core.tools import tool

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

@tool
def web_search(query: str) -> str:
    """Search the web for current information not available in the knowledge base — current events, prices, weather, anything outside NetsolTech's own documents."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": 5,
        "search_depth": "basic"
    }
    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    results = data.get("results", [])
    if not results:
        return "No search results found."
    formatted = [f"{r.get('title')}\n{r.get('content')}\n{r.get('url')}" for r in results]
    return "\n\n".join(formatted)