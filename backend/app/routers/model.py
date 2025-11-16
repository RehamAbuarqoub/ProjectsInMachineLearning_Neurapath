from fastapi import APIRouter
router = APIRouter(prefix="/model", tags=["model"])

@router.get("/status")
def status():
    return {"state": "ready", "note": "NER+semantic matching active. No supervised model required for UC-1."}
