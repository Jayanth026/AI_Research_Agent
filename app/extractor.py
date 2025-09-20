from __future__ import annotations
import io
import re
import requests
from typing import Tuple
from trafilatura import extract as trafi_extract
from pypdf import PdfReader

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
}

class ExtractError(Exception):
    pass

def _is_pdf(url: str, content_type: str | None) -> bool:
    if content_type and "pdf" in content_type.lower():
        return True
    return bool(re.search(r"\.pdf(\?.*)?$", url, flags=re.IGNORECASE))

def fetch_and_extract(url: str, max_chars: int = 15000) -> Tuple[str, str | None]:
    try:
        r = requests.get(url, timeout=40, headers=HEADERS)
    except requests.RequestException as e:
        return "", f"error: {e}"

    if r.status_code >= 400:
        if r.status_code in (401, 403):
            return "", "blocked"
        return "", f"error: HTTP {r.status_code}"

    ctype = r.headers.get("Content-Type")
    try:
        if _is_pdf(url, ctype):
            reader = PdfReader(io.BytesIO(r.content))
            pages = []
            for p in reader.pages[:20]:  # cap pages for demo
                try:
                    pages.append(p.extract_text() or "")
                except Exception:
                    pages.append("")
            text = "\n\n".join(pages).strip()
        else:
            text = trafi_extract(r.text, include_comments=False, favor_recall=True) or ""
    except Exception as e:
        return "", f"error: {e}"

    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return "", "empty"
    if len(text) > max_chars:
        text = text[:max_chars] + "\n... [truncated]"
    return text, None
