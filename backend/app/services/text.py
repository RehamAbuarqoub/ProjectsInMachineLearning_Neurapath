import re
from typing import List

def clean_text(t: str) -> str:
    t = (t or "").replace("\r", " ").replace("\n", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t

def redact_pii(t: str) -> str:
    t = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL]", t)
    t = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", t)
    return t

def find_spans(text: str, term: str) -> List[List[int]]:
    out = []
    for m in re.finditer(rf"\b{re.escape(term)}\b", text, flags=re.IGNORECASE):
        out.append([m.start(), m.end()])
    return out

def merge_spans(spans: List[List[int]]) -> List[List[int]]:
    if not spans: return []
    spans = sorted(spans)
    merged = [spans[0]]
    for s, e in spans[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return merged
