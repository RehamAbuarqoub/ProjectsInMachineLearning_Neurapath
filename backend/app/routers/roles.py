from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import json
import logging

# Use relative imports so this works when run as backend.app.main:app
from ..services.generator import ensure_models
from ..services.pipelines import SkillGapPipeline

logger = logging.getLogger("router.roles")

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

CATALOG_PATH, ROLES_PATH = ensure_models()
ROLES = json.loads(ROLES_PATH.read_text(encoding="utf-8"))

router = APIRouter(prefix="/roles", tags=["roles"])

# ------------------------------
# Existing endpoint: list roles
# ------------------------------
@router.get("")
def list_roles():
    """
    List all roles from the roles catalog.
    """
    logger.info("API /roles called - listing roles")
    return [
        {"role_id": k, "title": v["title"]}
        for k, v in ROLES.items()
    ]


# ------------------------------
# Assignment 6: Skill Gap MLOps Pipeline
# ------------------------------

# Initialize pipeline for Use Case 2 (Skill Gap + Recommendations)
skill_pipeline = SkillGapPipeline()


class SkillGapRequest(BaseModel):
    resume_text: str
    role_text: str


@router.post("/skill-gap/collect")
def skill_gap_collect():
    """
    Data Collection stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/collect called")
    data = skill_pipeline.collect_data()
    return {
        "status": "ok",
        "data_summary": {k: len(v) for k, v in data.items()}
    }


@router.post("/skill-gap/eda")
def skill_gap_eda():
    """
    EDA stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/eda called")
    data = skill_pipeline.collect_data()
    summary = skill_pipeline.run_eda(data)
    return {
        "status": "ok",
        "summary": summary
    }


@router.post("/skill-gap/preprocess")
def skill_gap_preprocess():
    """
    Preprocessing stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/preprocess called")
    data = skill_pipeline.collect_data()
    processed = skill_pipeline.preprocess(data)
    return {
        "status": "ok",
        "message": "preprocessing complete"
    }


@router.post("/skill-gap/train")
def skill_gap_train():
    """
    Training stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/train called")
    data = skill_pipeline.collect_data()
    processed = skill_pipeline.preprocess(data)
    metrics = skill_pipeline.train(processed)
    return {
        "status": "ok",
        "metrics": metrics
    }


@router.post("/skill-gap/validate")
def skill_gap_validate():
    """
    Validation stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/validate called")
    data = skill_pipeline.collect_data()
    processed = skill_pipeline.preprocess(data)
    results = skill_pipeline.validate(processed)
    return {
        "status": "ok",
        "results": results
    }


@router.post("/skill-gap/recommend")
def skill_gap_recommend(req: SkillGapRequest):
    """
    Serving / recommendation stage for Skill Gap pipeline.
    """
    logger.info("API /roles/skill-gap/recommend called")
    result = skill_pipeline.recommend(req.resume_text, req.role_text)
    return {
        "status": "ok",
        "result": result
    }
