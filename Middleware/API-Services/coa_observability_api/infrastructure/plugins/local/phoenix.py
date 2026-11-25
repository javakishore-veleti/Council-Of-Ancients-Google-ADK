"""Best-effort Phoenix plugin: log + optional OTLP HTTP push to Phoenix."""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from typing import ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)


class PhoenixPlugin(ObservabilityPlugin):
    """
    Phoenix primarily receives spans via OTLP (see OtelPlugin + PHOENIX_OTLP_ENDPOINT).

    This plugin additionally logs the feed and, when PHOENIX_HTTP_INGEST_URL is set,
    POSTs a best-effort JSON payload (soft-fail).
    """

    name: ClassVar[str] = "local.phoenix"
    domains: ClassVar[tuple[str, ...]] = ("traces", "llmops", "logs")

    def _emit(self, event: ObsFeedEvent) -> None:
        call = event.llm_call
        logger.info(
            "phoenix feed ingest_id=%s session_id=%s agent=%s model=%s",
            event.ingest_id,
            event.session_id,
            getattr(call, "agent", None),
            getattr(call, "model", None),
        )
        url = os.getenv("PHOENIX_HTTP_INGEST_URL")
        if not url:
            # Default: rely on OTEL dual-export; nothing else to do.
            return
        body = json.dumps(
            {
                "ingest_id": event.ingest_id,
                "session_id": event.session_id,
                "obs_data": event.obs_data,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                logger.debug("phoenix http ingest status=%s", resp.status)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.warning("phoenix http ingest soft-fail: %s", exc)
