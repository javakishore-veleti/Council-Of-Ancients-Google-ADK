"""Schemas for operationId deliberate."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeliberateRequest(BaseModel):
    session_id: str = Field(..., description="Council deliberation / portal session id")
    message: str = Field(..., min_length=1, description="User question or dilemma")
    user_id: str = Field(default="portal-user", description="End-user id for ADK session")
    ctx_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Open-ended context (labels, wave hints, client meta)",
    )


class DeliberateResponse(BaseModel):
    session_id: str
    reply: str
    events: list[dict[str, Any]] = Field(default_factory=list)
    status: str = "ok"
