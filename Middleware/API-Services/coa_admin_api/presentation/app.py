"""
FastAPI app: coa_admin_api (Admin BFF)

Run (from repo root):
  PYTHONPATH=Middleware/API-Services \\
    uv run uvicorn coa_admin_api.presentation.app:app --host 0.0.0.0 --port 8094
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from coa_admin_api.presentation.routes.endpoints import router as endpoints_router
from coa_admin_api.presentation.routes.sources import router as sources_router
from coa_admin_api.presentation.routes.wf_exec import router as wf_router

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Council of Ancients — Admin API",
    version="0.1.0",
    description=(
        "Admin BFF: knowledge sources, app endpoints, wf_exec_log. "
        "Admin UI talks only to this service (:8094)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:4201", "http://localhost:4201"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints_router)
app.include_router(sources_router)
app.include_router(wf_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
