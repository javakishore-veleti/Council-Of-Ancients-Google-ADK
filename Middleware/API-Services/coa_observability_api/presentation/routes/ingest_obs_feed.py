"""POST /v1/obs/feed — operationId: ingest_obs_feed."""

from __future__ import annotations

import logging

from fastapi import APIRouter, status

from coa_observability_api.application.facade.observability_facade import (
    get_observability_facade,
)
from coa_observability_api.presentation.schemas.ingest_obs_feed import (
    IngestObsFeedRequest,
    IngestObsFeedResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["observability"])


@router.post(
    "/v1/obs/feed",
    response_model=IngestObsFeedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="ingest_obs_feed",
    summary="Ingest observability feed (async fan-out)",
)
def ingest_obs_feed(body: IngestObsFeedRequest) -> IngestObsFeedResponse:
    """
    Accept observability feed; return 202 quickly.

    Fan-out runs in a background thread. Tasks run only when matching
    OBS_TASK_* env flags are true (default false). Soft-fails never raise here.
    """
    try:
        ingest_id = get_observability_facade().ingest(
            session_id=body.session_id,
            ctx_data=body.ctx_data,
        )
    except Exception:
        # Absolute soft-fail: still acknowledge so callers are never blocked.
        logger.exception("ingest_obs_feed unexpected error; returning synthetic id")
        import uuid

        ingest_id = str(uuid.uuid4())
    return IngestObsFeedResponse(ingest_id=ingest_id, status="accepted")
