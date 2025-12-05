# backend/app/main.py

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import datetime as dt
import logging

from .logging_config import configure_logging
from .config import settings
from .routers import roles, resumes, model, services_catalog


# ---------- Logging setup ----------
configure_logging()  # sets console + file handlers with required formatter
logger = logging.getLogger("neurapath.backend.main")


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

# If built frontend exists, serve it under "/static"
if FRONTEND_DIST.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
    logger.info("Mounted static frontend at '/static': %s", FRONTEND_DIST)


# ---------- Lifecycle ----------
@app.on_event("startup")
async def on_startup():
    """
    Startup hook: logs key experiment + DB config values
    using environment-based settings (for Secrets Management rubric).
    """
    # INFO #1 – high-level startup log
    logger.info("FastAPI startup complete. Logging configured and app ready.")

    # Log experiment / ML hyperparameters (SAFE – no passwords)
    logger.info(
        (
            "Experiment: %s (version=%s) | epochs=%d | "
            "expected_acc=%.3f | lr=%.6f | max_depth=%d | n_estimators=%d"
        ),
        settings.EXPERIMENT_NAME,
        settings.EXPERIMENT_VERSION,
        settings.MODEL_NUM_EPOCHS,
        settings.MODEL_EXPECTED_ACCURACY,
        settings.MODEL_LEARNING_RATE,
        settings.MODEL_MAX_DEPTH,
        settings.MODEL_N_ESTIMATORS,
    )

    # Log EDA features coming from env var
    logger.info("EDA feature names: %s", settings.EDA_FEATURE_NAMES)

    # ⚠️ Never log DB_PASSWORD
    logger.info(
        "DB config loaded (user=%s, host=%s, port=%d, password=HIDDEN)",
        settings.DB_USERNAME,
        settings.DB_HOST,
        settings.DB_PORT,
    )


# ---------- Health & root ----------
@app.get("/health")
def health():
    logger.info("Health check called.")  # INFO #2
    return {"ok": True, "ts": dt.datetime.utcnow().isoformat() + "Z"}


@app.get("/", include_in_schema=False)
def root():
    # If static isn't present (dev), redirect to docs
    if not FRONTEND_DIST.exists():
        logger.info("Root requested; static not found → redirecting to /docs.")  # INFO #3
        return RedirectResponse(url="/docs")
    # When static is present, you can later serve index.html explicitly if you want.
    # For now, just return 204 (no content).
    return Response(status_code=204)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


# ---------- Routers ----------
app.include_router(roles.router)
app.include_router(resumes.router)
app.include_router(model.router)
app.include_router(services_catalog.router)


# ---------- Dev entry ----------
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn in dev mode (reload=True).")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
