"""
FastAPI app: coa_agents_api

Run (from repo root):
  PYTHONPATH=Middleware/API-Services:Middleware:. \\
    uv run uvicorn coa_agents_api.presentation.app:app --host 0.0.0.0 --port 8090
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from coa_agents_api.presentation.routes.deliberate import router as deliberate_router

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Council of Ancients — Agents API",
    version="0.1.0",
    description=(
        "Facilitator + Plato / Descartes / Machiavelli via Google ADK. "
        "POST /v1/council/deliberate (operationId: deliberate). "
        "Each model turn emits into coa_observability_api facade (OBS_TASK_* gated)."
    ),
)

app.include_router(deliberate_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
