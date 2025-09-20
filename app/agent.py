from __future__ import annotations
from sqlalchemy.orm import Session
from typing import List, Dict
from .search import tavily_search, SearchError
from .extractor import fetch_and_extract
from .llm import summarize_with_openai, LLMError
from .models import Report, Source

class Agent:
    def __init__(self, db: Session):
        self.db = db

    def run(self, query: str) -> Report:
        # 1) Search
        try:
            raw_results = tavily_search(query, max_results=3)
        except SearchError as e:
            r = Report(query=query, summary_md=f"# Search failed\n\n> {e}")
            self.db.add(r)
            self.db.commit()
            return r

        # 2) Extract content
        sources: List[Dict] = []
        for idx, item in enumerate(raw_results, start=1):
            label = f"S{idx}"
            text, note = fetch_and_extract(item["url"])  # note may be None / "blocked" / etc.
            status = "ok" if note is None else ("blocked" if note == "blocked" else "error")
            if note == "empty":
                status = "skipped"
            sources.append({
                "label": label,
                "title": item.get("title"),
                "url": item["url"],
                "text": text,
                "status": status,
                "note": note,
            })

        # 3) Summarize with LLM
        try:
            md = summarize_with_openai(query, sources)
        except LLMError as e:
            md = f"# Summarization failed\n\nQuery: {query}\n\n> {e}"

        # 4) Save report + sources
        report = Report(query=query, summary_md=md)
        self.db.add(report)
        self.db.flush()  # get report.id

        for s in sources:
            src = Source(
                report_id=report.id,
                title=s.get("title"),
                url=s["url"],
                status=s.get("status") or "ok",
                note=s.get("note"),
            )
            self.db.add(src)
        self.db.commit()

        return report
