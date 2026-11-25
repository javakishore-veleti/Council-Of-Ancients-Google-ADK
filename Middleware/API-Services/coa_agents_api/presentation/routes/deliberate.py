"""POST /v1/council/deliberate — operationId: deliberate."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from coa_agents_api.application.deliberation_service import deliberate
from coa_agents_api.presentation.schemas.deliberate import (
    DeliberateRequest,
    DeliberateResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["council"])


@router.post(
    "/v1/council/deliberate",
    response_model=DeliberateResponse,
    status_code=status.HTTP_200_OK,
    operation_id="deliberate",
    summary="Run a Council of Ancients deliberation turn",
)
async def deliberate_endpoint(body: DeliberateRequest) -> DeliberateResponse:
    result = await deliberate(
        session_id=body.session_id,
        message=body.message,
        user_id=body.user_id,
        ctx_data=body.ctx_data,
    )
    return DeliberateResponse(
        session_id=result["session_id"],
        reply=result["reply"],
        events=result.get("events") or [],
        status=result.get("status") or "ok",
    )
