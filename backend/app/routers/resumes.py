from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid, json
from statistics import mean

from app.services.text import clean_text, redact_pii, find_spans, merge_spans
from app.services.generator import ensure_models
from app.services.io_extract import extract_text
from app.services.bert_ner import BertSkillNER
from app.services.semantic import SemanticSkillMatcher

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
STORE_DIR = APP_DIR / "storage"
STORE_DIR.mkdir(parents=True, exist_ok=True)

CATALOG_PATH, ROLES_PATH = ensure_models()
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
ROLES   = json.loads(ROLES_PATH.read_text(encoding="utf-8"))

NER      = BertSkillNER(CATALOG)           # stricter thresholds live inside service modules
SEMANTIC = SemanticSkillMatcher(CATALOG)

router = APIRouter(prefix="/resumes", tags=["resumes"])

def _score_against_role(extracted_set, evidence_scores, role_obj):
    req = set(role_obj.get("required_skills", []))
    nice = set(role_obj.get("nice_to_have_skills", []))
    if not req and not nice:
        return 0.0, 0.0, 0.0
    req_cov = (len(extracted_set & req) / max(1, len(req))) if req else 0.0
    nice_cov = (len(extracted_set & nice) / max(1, len(nice))) if nice else 0.0
    ev_present = [evidence_scores.get(s, 0.0) for s in extracted_set if s in evidence_scores]
    ev_bonus = mean(ev_present) if ev_present else 0.0  # 0..1 approx
    base = 0.70 * req_cov + 0.30 * nice_cov
    score = base * 100.0
    # clamp alias/NER bonus to small range
    score += min(10.0, max(0.0, ev_bonus) * 10.0)
    return round(max(0.0, min(100.0, score)), 1), round(req_cov, 3), round(nice_cov, 3)

def _suitability_label(score):
    if score >= 80: return "Excellent"
    if score >= 60: return "Good"
    if score >= 40: return "Fair"
    return "Low"

@router.post("")
async def upload_resume(file: UploadFile = File(...), role_id: str = Form(None)):
    rid = str(uuid.uuid4())[:8]
    fpath = STORE_DIR / f"{rid}_{file.filename}"
    fpath.write_bytes(await file.read())

    # Parse -> text
    raw = extract_text(fpath)
    text = redact_pii(clean_text(raw))

    # 1) Alias evidence (strictly clamped)
    enriched = {}
    for canon, aliases in CATALOG.items():
        spans = []
        for a in aliases:
            spans += find_spans(text, a)
        spans = merge_spans(spans)
        if spans:
            enriched[canon] = {
                "skill": canon,
                # clamp to [0,1] so UI never shows 3.75 etc.
                "score": min(1.0, round(0.4 + 0.2 * len(spans), 2)),
                "evidence_offsets": spans,
                "aliases_matched": [a for a in aliases if find_spans(text, a)]
            }

    present = set(enriched.keys())

    # 2) BERT NER → SBERT map (threshold stricter inside service)
    ner_terms = NER.extract_terms(text)
    for lab, score in NER.map_to_skills(ner_terms, threshold=0.65):  # stricter here too
        if lab not in present:
            enriched[lab] = {
                "skill": lab,
                "score": min(1.0, round(0.58 + 0.25 * (score - 0.58) / (1.0 - 0.58), 2)),
                "evidence_offsets": [],
                "aliases_matched": []
            }
            present.add(lab)

    # 3) SBERT semantic on whole text (stricter threshold)
    for lab, score in SEMANTIC.predict(text, top_k=6, threshold=0.62):
        if lab not in present:
            enriched[lab] = {
                "skill": lab,
                "score": min(1.0, round(0.56 + 0.22 * (score - 0.56) / (1.0 - 0.56), 2)),
                "evidence_offsets": [],
                "aliases_matched": []
            }
            present.add(lab)

    # Collate
    skills = sorted(enriched.values(), key=lambda x: x["score"], reverse=True)
    extracted_set = {s["skill"] for s in skills}
    evidence_scores = {s["skill"]: min(1.0, max(0.0, s["score"])) for s in skills}

    # Score all roles, pick primary, compute gaps, and recommendations
    scored_roles = []
    for rid_key, role_obj in ROLES.items():
        score, req_cov, nice_cov = _score_against_role(extracted_set, evidence_scores, role_obj)
        scored_roles.append({
            "role_id": rid_key,
            "title": role_obj["title"],
            "score": score,
            "suitability": _suitability_label(score),
            "required_coverage": req_cov,
            "nice_coverage": nice_cov,
        })
    scored_roles.sort(key=lambda r: r["score"], reverse=True)

    if role_id in ROLES:
        primary = next((r for r in scored_roles if r["role_id"] == role_id), scored_roles[0] if scored_roles else None)
    else:
        primary = scored_roles[0] if scored_roles else None

    gaps = []
    if primary:
        role_obj = ROLES[primary["role_id"]]
        required = role_obj.get("required_skills", [])
        gaps_list = [r for r in required if r.lower() not in {x.lower() for x in extracted_set}]
        gaps = [{"skill": g, "priority": i + 1} for i, g in enumerate(gaps_list)]

    other_recs = [r for r in scored_roles if primary and r["role_id"] != primary["role_id"]][:5]
    no_good_match = (primary is None) or (primary["score"] < 35.0)

    bullets = []
    if skills:
        bullets.append(f"Strengths detected: {', '.join([s['skill'] for s in skills[:6]])}.")
    if gaps:
        bullets.append(f"Improve match by adding: {', '.join([g['skill'] for g in gaps[:5]])}.")
    bullets += [
        "Action: Keep a focused 'Skills' section (8–12 items) with versions (e.g., Python 3.11).",
        "Action: Use Goal → Tools → Impact bullets and add metrics."
    ]

    resp = {
        "resume_id": rid,
        "extract_id": str(uuid.uuid4())[:8],
        "selected_role": primary,
        "other_recommendations": other_recs,
        "no_good_match": no_good_match,
        "skills": skills,
        "gaps": gaps,
        "critique": {
            "summary": f"Match to '{primary['title']}' is {primary['score']}% ({primary['suitability']})." if primary else "No role found.",
            "bullets": bullets,
            "tone": "supportive"
        },
        "text_preview": text[:1200],
        "model_ver": "bert-ner+semantic+alias-v2.1"
    }

    (STORE_DIR / f"{rid}_extraction.json").write_text(json.dumps(resp, indent=2), encoding="utf-8")
    return JSONResponse(resp)
