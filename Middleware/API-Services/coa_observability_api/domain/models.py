"""Domain models for observability feed ingest."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class LLMCallObs:
    """Normalized LLM call fields extracted from obs_data (best-effort)."""

    agent: str = "unknown"
    model: str = "unknown"
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_seconds: float = 0.0
    ttft_seconds: float | None = None
    started_at_unix: float | None = None
    first_token_at_unix: float | None = None
    ended_at_unix: float | None = None
    status: str = "ok"
    deliberation_wave: str | None = None
    event_type: str = "llm_call"

    @property
    def total_tokens(self) -> int:
        return int(self.prompt_tokens) + int(self.completion_tokens)

    @classmethod
    def from_obs_data(cls, obs_data: Mapping[str, Any] | None) -> LLMCallObs | None:
        if not obs_data:
            return None
        event_type = str(obs_data.get("event_type") or obs_data.get("type") or "llm_call")
        if event_type not in ("llm_call", "llm", "generation"):
            # Still allow generic payloads; treat as llm_call if token/model keys present.
            if not any(
                k in obs_data
                for k in ("model", "prompt_tokens", "completion_tokens", "agent")
            ):
                return None
        return cls(
            agent=str(obs_data.get("agent") or "unknown"),
            model=str(obs_data.get("model") or "unknown"),
            prompt_tokens=int(obs_data.get("prompt_tokens") or 0),
            completion_tokens=int(obs_data.get("completion_tokens") or 0),
            duration_seconds=float(obs_data.get("duration_seconds") or 0.0),
            ttft_seconds=(
                float(obs_data["ttft_seconds"])
                if obs_data.get("ttft_seconds") is not None
                else None
            ),
            started_at_unix=(
                float(obs_data["started_at_unix"])
                if obs_data.get("started_at_unix") is not None
                else None
            ),
            first_token_at_unix=(
                float(obs_data["first_token_at_unix"])
                if obs_data.get("first_token_at_unix") is not None
                else None
            ),
            ended_at_unix=(
                float(obs_data["ended_at_unix"])
                if obs_data.get("ended_at_unix") is not None
                else None
            ),
            status=str(obs_data.get("status") or "ok"),
            deliberation_wave=(
                str(obs_data["deliberation_wave"])
                if obs_data.get("deliberation_wave") is not None
                else None
            ),
            event_type=event_type,
        )


@dataclass
class ObsFeedEvent:
    """One accepted observability feed ingest."""

    ingest_id: str
    session_id: str
    ctx_data: dict[str, Any] = field(default_factory=dict)
    obs_data: dict[str, Any] = field(default_factory=dict)

    @property
    def llm_call(self) -> LLMCallObs | None:
        return LLMCallObs.from_obs_data(self.obs_data)
