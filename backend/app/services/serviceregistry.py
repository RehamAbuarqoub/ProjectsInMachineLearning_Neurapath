from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import json
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

CANDIDATE_FILES = [
    "MLOps_UseCase_API_Design_Neurapath_v1.csv",
    "MLOps_UseCase_API_Design_Neurapath_v1.xlsx",
    "services_catalog.csv",
    "services_catalog.xlsx",
]

CANON_KEYS = {
    "service_name": ["service_name", "name", "api_name", "service"],
    "method": ["method", "http_method", "verb"],
    "path": ["path", "endpoint", "route", "url"],
    "summary": ["summary", "description", "desc"],
    "request_schema": ["request_schema", "request", "request_fields", "request_body"],
    "response_schema": ["response_schema", "response", "response_fields", "response_body"],
    "owner": ["owner", "team", "contact"],
    "version": ["version", "ver"],
    "tags": ["tags", "label", "labels"]
}

def _find_file() -> Path | None:
    for name in CANDIDATE_FILES:
        p = DATA_DIR / name
        if p.exists():
            return p
    return None

def _read_table(p: Path) -> pd.DataFrame:
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p)
    if p.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(p, engine="openpyxl")
    raise ValueError(f"Unsupported service file type: {p.suffix}")

def _norm_header(col: str) -> str:
    c = (col or "").strip().lower().replace(" ", "").replace("-", "").replace("_", "")
    return c

def _canon_map(df: pd.DataFrame) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    df_cols = { _norm_header(c): c for c in df.columns }
    for canon, variants in CANON_KEYS.items():
        for v in variants:
            key = _norm_header(v)
            if key in df_cols:
                mapping[canon] = df_cols[key]
                break
    return mapping

def _coerce_jsonish(x: Any) -> Any:
    if isinstance(x, (dict, list)) or pd.isna(x):
        return x if not pd.isna(x) else None
    s = str(x).strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s

def load_services() -> List[Dict[str, Any]]:
    p = _find_file()
    if not p:
        return []
    df = _read_table(p)
    if df.empty:
        return []

    mapping = _canon_map(df)
    required = ("service_name", "method", "path")
    if not all(k in mapping for k in required):
        cols = list(df.columns)
        if len(cols) >= 3:
            mapping["service_name"], mapping["method"], mapping["path"] = cols[:3]
        else:
            return []

    out: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        rec = {}
        for canon, col in mapping.items():
            rec[canon] = row.get(col, None)
        rec["method"] = str(rec.get("method") or "").strip().upper() or "GET"
        rec["path"] = str(rec.get("path") or "").strip()
        rec["service_name"] = str(rec.get("service_name") or "").strip()
        rec["request_schema"] = _coerce_jsonish(rec.get("request_schema"))
        rec["response_schema"] = _coerce_jsonish(rec.get("response_schema"))
        rec["tags"] = _coerce_jsonish(rec.get("tags"))
        out.append(rec)
    out = [r for r in out if r["service_name"] and r["path"]]
    return out
