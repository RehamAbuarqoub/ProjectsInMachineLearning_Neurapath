from pathlib import Path
from collections import Counter
from typing import Dict, List, Set
import pandas as pd
import json, re

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_PATH = DATA_DIR / "job_skill_data.csv"
CATALOG_PATH = DATA_DIR / "skills_catalog.json"
ROLES_PATH = DATA_DIR / "role_templates.json"

# expanded stopwords (avoid common junk like 'a', 'the', 'experience', etc.)
STOP: Set[str] = {
    "", "a", "an", "the", "and", "or", "with", "using", "of", "to", "for", "in", "on",
    "experience", "developer", "engineer", "junior", "senior", "degree", "team", "work",
    "environment", "etc", "skills", "proficient", "knowledge", "strong", "familiar",
    "good", "excellent", "expert"
}

def _normalize(s: str) -> str:
    if not isinstance(s, str): return ""
    s = re.sub(r"\s+", " ", s.strip().lower()).strip(" .,:;()[]{}<>*'\"")
    return s

def _looks_like_version(tok: str) -> bool:
    # e.g., 3, 3.11, v2, 2023, 1.x
    if re.fullmatch(r"v?\d+(\.\d+)*", tok): return True
    if re.fullmatch(r"\d{4}", tok): return True  # pure year
    return False

def _is_valid_skill_token(tok: str) -> bool:
    # reject 1-char tokens (kills 'a'), and long garbage
    if not (2 <= len(tok) <= 50):
        return False
    if tok in STOP:
        return False
    if _looks_like_version(tok):
        return False
    # reject tokens that are ≥50% digits
    digits = sum(c.isdigit() for c in tok)
    if digits >= max(2, int(0.5*len(tok))):
        return False
    return True

def _tokenize_skills(raw: str) -> List[str]:
    if not isinstance(raw, str): return []
    # split on common list delimiters
    parts = re.split(r"[,\|/•;·\n\r]+", raw)
    out = []
    for p in parts:
        t = _normalize(p)
        if _is_valid_skill_token(t):
            out.append(t)
    return out

def _aliases(canon: str) -> List[str]:
    al = {canon, canon.replace(".", ""), canon.replace(" ", "")}
    if canon == "node.js": al.add("nodejs")
    if canon in {"ml ops", "m l ops"}: al.update({"mlops", "ml-ops"})
    return sorted(al)

def build_from_dataset(top_skills: int = 1000, per_role_limit: int = 30):
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Dataset missing: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    for col in ("job_title", "job_skills"):
        if col not in df.columns:
            raise ValueError("CSV must contain columns: job_title, job_skills")

    # Build global skill vocab
    global_freq = Counter()
    for s in df["job_skills"]:
        global_freq.update(_tokenize_skills(s))
    vocab = [s for s, _ in global_freq.most_common(top_skills)]
    catalog: Dict[str, List[str]] = {canon: _aliases(canon) for canon in vocab}

    # Include ALL titles (normalized)
    df["_norm_title"] = df["job_title"].astype(str).apply(_normalize)
    norm_to_display = {}
    for t in df["job_title"].astype(str).unique():
        norm_to_display[_normalize(t)] = t

    # Aggregate skills per role
    roles = {}
    for norm_title, sub in df.groupby("_norm_title", dropna=False):
        if not norm_title:
            continue
        local = Counter()
        for s in sub["job_skills"]:
            local.update([x for x in _tokenize_skills(s) if x in catalog])
        ranked = [s for s, _ in local.most_common(per_role_limit)]
        required = ranked[: max(12, per_role_limit // 2)]
        nice = [r for r in ranked if r not in required]
        role_id = re.sub(r"[^a-z0-9]+", "_", norm_title).strip("_").upper()[:48]
        roles[role_id] = {
            "title": norm_to_display.get(norm_title, norm_title).strip(),
            "required_skills": required,
            "nice_to_have_skills": nice
        }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    ROLES_PATH.write_text(json.dumps(roles, indent=2), encoding="utf-8")
    return CATALOG_PATH, ROLES_PATH

def ensure_models():
    if not CATALOG_PATH.exists() or not ROLES_PATH.exists():
        return build_from_dataset()
    return CATALOG_PATH, ROLES_PATH
