from fastapi import APIRouter
from typing import List, Dict, Any
from app.services.serviceregistry import load_services

router = APIRouter(prefix="/services", tags=["services"])

@router.get("", response_model=List[Dict[str, Any]])
def list_services():
    return load_services()

@router.get("/ping")
def ping():
    return {"ok": True}
