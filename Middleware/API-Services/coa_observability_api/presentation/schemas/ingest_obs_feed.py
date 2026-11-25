"""Schemas for operationId ingest_obs_feed."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IngestObsFeedRequest(BaseModel):
    """
    Body: { session_id, ctx_data: { ..., obs_data: { ... } } }

    `obs_data` is a child of `ctx_data` (not a top-level sibling).
    """

    session_id: str = Field(..., min_length=1, description="Caller session identifier")
    ctx_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Context bag; nest observability payload under ctx_data.obs_data",
    )


class IngestObsFeedResponse(BaseModel):
    ingest_id: str
    status: str = "accepted"
