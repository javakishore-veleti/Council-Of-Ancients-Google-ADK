from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class KnowledgeCategory:
    id: UUID
    code: str
    name: str
    description: str | None
    parent_id: UUID | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class KnowledgeSource:
    id: UUID
    category_id: UUID
    name: str
    description: str | None
    citation_name: str
    citation_desc: str | None
    source_key: str
    url: str | None
    license: str | None
    status: str
    meta: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
