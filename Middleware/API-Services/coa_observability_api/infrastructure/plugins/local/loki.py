"""Best-effort Loki plugin: push JSON log lines via Loki HTTP API when reachable."""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from typing import ClassVar

from coa_observability_api.domain.models import ObsFeedEvent
from coa_observability_api.infrastructure.plugins.base import ObservabilityPlugin

logger = logging.getLogger(__name__)


class LokiPlugin(ObservabilityPlugin):
    name: ClassVar[str] = "local.loki"
    domains: ClassVar[tuple[str, ...]] = ("logs",)

    def _emit(self, event: ObsFeedEvent) -> None:
        base = (os.getenv("LOKI_URL") or "http://localhost:3100").rstrip("/")
        push_url = f"{base}/loki/api/v1/push"
        call = event.llm_call
        line = {
            "ingest_id": event.ingest_id,
            "session_id": event.session_id,
            "obs_data": event.obs_data,
        }
        if call is not None:
            line.update(
                {
                    "agent": call.agent,
                    "model": call.model,
                    "status": call.status,
                    "prompt_tokens": call.prompt_tokens,
                    "completion_tokens": call.completion_tokens,
                }
            )
        ns = str(int(time.time() * 1e9))
        payload = {
            "streams": [
                {
                    "stream": {
                        "job": "coa-observability-api",
                        "service": "council-of-ancients",
                        "level": "info",
                    },
                    "values": [[ns, json.dumps(line, default=str)]],
                }
            ]
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            push_url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                logger.debug("loki push status=%s ingest_id=%s", resp.status, event.ingest_id)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            logger.warning(
                "loki push soft-fail ingest_id=%s err=%s (logged locally)",
                event.ingest_id,
                exc,
            )
            logger.info("loki-local-fallback %s", json.dumps(line, default=str))
