# backend/app/main.py
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import datetime as dt
import logging

# ✅ logging (formatter: "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
from .logging_config import configure_logging  # keep relative import

# ✅ routers
from .routers import roles, resumes, model, services_catalog

# ---------- Logging setup ----------
configure_logging()  # sets console + file handlers with required formatter
log = logging.getLogger("app.main")

# ---------- App & static (built frontend) ----------
app = FastAPI(
    title="NeuraPath UC-1 (BERT NER + Semantic + Service Catalog)",
    version="1.0.0",
)

# CORS: allow frontend (React/Vite) to call the API during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "static"  # Docker copies React build here

# If built frontend exists, serve it as a SPA at "/"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
    log.info("Mounted static frontend at '/': %s", FRONTEND_DIST)

# ---------- Lifecycle ----------
@app.on_event("startup")
async def on_startup():
    log.info("FastAPI startup complete. Logging configured and app ready.")  # INFO #1

# ---------- Health & root ----------
@app.get("/health")
def health():
    log.info("Health check called.")  # INFO #2
    return {"ok": True, "ts": dt.datetime.utcnow().isoformat() + "Z"}

@app.get("/", include_in_schema=False)
def root():
    # If static isn't present (dev), redirect to docs
    if not FRONTEND_DIST.exists():
        log.info("Root requested; static not found → redirecting to /docs.")  # INFO #3
        return RedirectResponse(url="/docs")
    # When static is mounted, index.html is served by StaticFiles
    return Response(status_code=204)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

# ---------- Routers ----------
app.include_router(roles.router)
app.include_router(resumes.router)         # resumes.py already logs INFO during analysis
app.include_router(model.router)
app.include_router(services_catalog.router)

# ---------- Dev entry ----------
if __name__ == "__main__":
    import uvicorn
    log.info("Starting Uvicorn in dev mode (reload=True).")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
