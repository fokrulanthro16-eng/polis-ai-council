"""POLIS backend entrypoint: FastAPI app wiring, CORS, and health check."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as council_router
from app.config import settings

app = FastAPI(
    title="POLIS - Collective Intelligence API",
    description="Multi-agent council that debates a problem and returns a transparent consensus.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(council_router)


@app.get("/")
def root():
    return {"service": "polis-backend", "status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
