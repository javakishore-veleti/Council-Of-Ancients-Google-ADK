"""
FastAPI app: coa_observability_api

Run (from repo root):
  PYTHONPATH=Middleware/API-Services:. \\
    uv run uvicorn coa_observability_api.presentation.app:app --host 0.0.0.0 --port 8088
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI

from coa_observability_api.presentation.routes.ingest_obs_feed import router as ingest_router

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Council of Ancients — Observability API",
    version="0.1.0",
    description=(
        "Async observability ingest. POST /v1/obs/feed (operationId: ingest_obs_feed) "
        "returns 202; fan-out is gated by OBS_TASK_EMIT_* env flags (default off)."
    ),
)

app.include_router(ingest_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
