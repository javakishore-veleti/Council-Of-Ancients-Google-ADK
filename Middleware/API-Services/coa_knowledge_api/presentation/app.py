"""
FastAPI app: coa_knowledge_api (Knowledge Bank)

Run (from repo root):
  PYTHONPATH=Middleware/API-Services \\
    uv run uvicorn coa_knowledge_api.presentation.app:app --host 0.0.0.0 --port 8093
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from coa_knowledge_api.presentation.routes.categories import router as categories_router
from coa_knowledge_api.presentation.routes.sources import router as sources_router

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Council of Ancients — Knowledge Bank API",
    version="0.1.0",
    description=(
        "CRUD for knowledge_category (top-nav topics + left-nav sections) and "
        "knowledge_source (allowlisted corpus with citation_name / citation_desc for indexing)."
    ),
)

app.include_router(categories_router)
app.include_router(sources_router)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}
