from __future__ import annotations
import os
from typing import List, Dict
import re
from openai import OpenAI

class LLMError(Exception):
    pass

SYSTEM = (
    "You are a careful research assistant. You write concise, structured markdown reports with clear headings,"
    " bullet points, and short sentences. You cite sources by label only (we will insert links in UI)."
)

TEMPLATE = (
    "Create a short, structured report in Markdown with these sections: \n"
    "# Title\n"
    "**Query:** <the user's query>\n"
    "**Date:** <today's date>\n\n"
    "## Key Findings\n- 4–8 bullets with crisp, evidence-backed points.\n\n"
    "## Where Sources Agree\n- 2–4 bullets.\n\n"
    "## Caveats & Gaps\n- 2–4 bullets highlighting limitations or disagreements.\n\n"
    "## Sources\n- Simply list the titles of the sources provided (no [S1], [S2], [S3] labels)."
)

def linkify_citations(md: str, sources: List[Dict]) -> str:
    for s in sources:
        label = s["label"]
        md = re.sub(rf"\[{label}\]", f'<a href="#{label}">[{label}]</a>', md)
    return md

def summarize_with_openai(query: str, sources: List[Dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("Missing OPENAI_API_KEY.")

    client = OpenAI(api_key=api_key)

    src_chunks = []
    for s in sources:
        head = f"[{s['label']}] {s.get('title') or '(No title)'} — {s['url']}".strip()
        body = s.get("text") or "(no extractable text)"
        src_chunks.append(f"{head}\n\n{body}")
    src_text = "\n\n---\n\n".join(src_chunks)

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"QUERY:\n{query}\n\nSOURCES:\n{src_text}\n\nINSTRUCTIONS:\n{TEMPLATE}"},
    ]

    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.2,
        )
        result = resp.choices[0].message.content.strip()
        return linkify_citations(result, sources)
    except Exception as e:
        raise LLMError(str(e))
