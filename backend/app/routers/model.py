from fastapi import APIRouter
from pydantic import BaseModel
import logging

from ..services.pipelines import ResumeMatchPipeline

# Keep the same prefix you already use so existing frontend calls still work
router = APIRouter(prefix="/model", tags=["model"])

logger = logging.getLogger("router.model")

# Initialize pipeline for Use Case 1 (Resume–Job Match)
pipeline = ResumeMatchPipeline()


# ------------------------------
# Existing endpoint from your app
# ------------------------------
@router.get("/status")
def status():
    return {
        "state": "ready",
        "note": "NER + semantic matching active. No supervised model required for UC-1."
    }


# ------------------------------
# Assignment 6: Resume Match MLOps Pipeline
# ------------------------------

class ResumeMatchRequest(BaseModel):
    resume_text: str
    role_text: str


@router.post("/resume-match/collect")
def collect_resume_match():
    """
    Data Collection stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/collect called")
    data = pipeline.collect_data()
    return {
        "status": "ok",
        "data_summary": {k: len(v) for k, v in data.items()}
    }


@router.post("/resume-match/eda")
def resume_match_eda():
    """
    EDA stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/eda called")
    data = pipeline.collect_data()
    summary = pipeline.run_eda(data)
    return {
        "status": "ok",
        "summary": summary
    }


@router.post("/resume-match/preprocess")
def resume_match_preprocess():
    """
    Preprocessing stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/preprocess called")
    data = pipeline.collect_data()
    processed = pipeline.preprocess(data)
    # We don't need to return the full processed data, just a status
    return {
        "status": "ok",
        "message": "preprocessing complete"
    }


@router.post("/resume-match/train")
def resume_match_train():
    """
    Training stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/train called")
    data = pipeline.collect_data()
    processed = pipeline.preprocess(data)
    metrics = pipeline.train(processed)
    return {
        "status": "ok",
        "metrics": metrics
    }


@router.post("/resume-match/validate")
def resume_match_validate():
    """
    Validation stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/validate called")
    data = pipeline.collect_data()
    processed = pipeline.preprocess(data)
    results = pipeline.validate(processed)
    return {
        "status": "ok",
        "results": results
    }


@router.post("/resume-match/predict")
def resume_match_predict(request: ResumeMatchRequest):
    """
    Serving / prediction stage for Resume–Job Match pipeline.
    """
    logger.info("API /model/resume-match/predict called")
    prediction = pipeline.predict(request.resume_text, request.role_text)
    return {
        "status": "ok",
        "prediction": prediction
    }
