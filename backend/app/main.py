try:
    from app.routers import roles, resumes, model, services_catalog
except ModuleNotFoundError:
    import sys, pathlib
    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT))
    from routers import roles, resumes, model, services_catalog  # type: ignore

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import datetime as dt

app = FastAPI(title="NeuraPath UC-1 (BERT NER + Semantic + Service Catalog)", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.get("/health")
def health(): return {"ok": True, "ts": dt.datetime.utcnow().isoformat()+"Z"}

@app.get("/", include_in_schema=False)
def root(): return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon(): return Response(status_code=204)

app.include_router(roles.router)
app.include_router(resumes.router)
app.include_router(model.router)
app.include_router(services_catalog.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
