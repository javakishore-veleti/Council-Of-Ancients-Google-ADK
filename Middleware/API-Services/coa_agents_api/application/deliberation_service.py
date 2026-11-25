"""Run Facilitator via ADK InMemoryRunner; emit obs via model callbacks."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from google.adk.runners import InMemoryRunner
from google.genai import types

logger = logging.getLogger(__name__)

_runner: InMemoryRunner | None = None


def _ensure_repo_paths() -> None:
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[4]
    middleware = repo_root / "Middleware"
    agents = middleware / "Agents"
    for p in (str(repo_root), str(middleware), str(agents)):
        if p not in sys.path:
            sys.path.insert(0, p)


def _get_runner() -> InMemoryRunner:
    """Process-wide runner so ADK sessions survive across HTTP requests."""
    global _runner
    if _runner is None:
        _ensure_repo_paths()
        from Middleware.Agents.council_of_ancients.agent import app as council_app

        _runner = InMemoryRunner(app=council_app)
    return _runner


def _extract_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    parts = getattr(content, "parts", None)
    if parts is None and isinstance(content, dict):
        parts = content.get("parts") or []
    parts = parts or []
    chunks: list[str] = []
    for part in parts:
        if isinstance(part, str):
            chunks.append(part)
            continue
        if isinstance(part, dict):
            text = part.get("text")
        else:
            text = getattr(part, "text", None)
        if text:
            chunks.append(str(text))
    return "\n".join(chunks).strip()


def _is_final(event: Any) -> bool:
    fn = getattr(event, "is_final_response", None)
    if callable(fn):
        try:
            return bool(fn())
        except Exception:
            return False
    return bool(fn)


async def deliberate(
    *,
    session_id: str,
    message: str,
    user_id: str = "portal-user",
    ctx_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Run one council turn.

    Observability: each model call hits after_model_callback → record_llm_call
    → HTTP POST COA_OBS_API_URL /v1/obs/feed (fallback: in-process facade).
    """
    _ensure_repo_paths()
    from Middleware.Agents.council_of_ancients.observability_hooks import (
        obs_session_id,
        obs_wave,
    )
    from Middleware.Observability.llmops import setup_observability

    setup_observability(service_name="coa_agents_api")

    sid = session_id or str(uuid.uuid4())
    wave = None
    if ctx_data:
        wave = ctx_data.get("wave") or ctx_data.get("deliberation_wave")

    tok_s = obs_session_id.set(sid)
    tok_w = obs_wave.set(wave if isinstance(wave, str) else None)
    started = time.time()
    events_out: list[dict[str, Any]] = []
    final_text = ""

    try:
        runner = _get_runner()
        council_app = runner.app if getattr(runner, "app", None) else None
        app_name = getattr(council_app, "name", None) or getattr(
            runner, "app_name", "council_of_ancients"
        )

        existing = await runner.session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=sid,
        )
        if existing is None:
            await runner.session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=sid,
            )

        new_message = types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=sid,
            new_message=new_message,
        ):
            author = getattr(event, "author", None) or getattr(event, "node_name", None)
            text = _extract_text(getattr(event, "content", None))
            is_final = _is_final(event)
            entry = {
                "author": author,
                "is_final": is_final,
                "text": text,
            }
            if text:
                events_out.append(entry)
                # Prefer facilitator finals; otherwise last textual event.
                if is_final and (
                    author in (None, "facilitator") or not final_text
                ):
                    final_text = text
                elif not final_text:
                    final_text = text
                elif author == "facilitator":
                    final_text = text

        if not final_text and events_out:
            final_text = events_out[-1].get("text") or ""

        return {
            "session_id": sid,
            "reply": final_text or "(no text response)",
            "events": events_out,
            "status": "ok",
            "duration_seconds": max(0.0, time.time() - started),
        }
    except Exception as exc:
        logger.exception("deliberate failed session_id=%s", sid)
        return {
            "session_id": sid,
            "reply": f"Council deliberation failed: {exc}",
            "events": events_out,
            "status": "error",
            "duration_seconds": max(0.0, time.time() - started),
        }
    finally:
        obs_session_id.reset(tok_s)
        obs_wave.reset(tok_w)
