from __future__ import annotations
import os
import requests

TAVILY_ENDPOINT = "https://api.tavily.com/search"

class SearchError(Exception):
    pass

def tavily_search(query: str, max_results: int = 3) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise SearchError("Missing TAVILY_API_KEY.")

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
    }
    try:
        r = requests.post(TAVILY_ENDPOINT, json=payload, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        raise SearchError(f"Search failed: {e}")

    data = r.json()
    results = data.get("results", [])
    cleaned = []
    for res in results:
        cleaned.append({
            "title": res.get("title") or "(No title)",
            "url": res.get("url"),
            "snippet": res.get("content") or "",
        })
    if not cleaned:
        raise SearchError("No results found.")
    return cleaned[:max_results]
