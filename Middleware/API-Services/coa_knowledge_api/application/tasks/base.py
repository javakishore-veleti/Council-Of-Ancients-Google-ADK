"""Base knowledge task — thin application step between facade and sub-facade."""

from __future__ import annotations

from abc import ABC


class BaseKnowledgeTask(ABC):
    name: str = "knowledge_task"
