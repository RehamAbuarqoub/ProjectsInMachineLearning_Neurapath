from fastapi import APIRouter
from pathlib import Path
import json
from app.services.generator import ensure_models

APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"

CATALOG_PATH, ROLES_PATH = ensure_models()
ROLES = json.loads(ROLES_PATH.read_text(encoding="utf-8"))

router = APIRouter(prefix="/roles", tags=["roles"])

@router.get("")
def list_roles():
    return [{"role_id": k, "title": v["title"]} for k, v in ROLES.items()]
