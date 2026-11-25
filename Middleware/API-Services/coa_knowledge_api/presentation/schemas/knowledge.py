from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=128)
    name: str = Field(..., min_length=1, max_length=256)
    description: str | None = None
    parent_id: UUID | None = None
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=256)
    description: str | None = None
    parent_id: UUID | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryOut(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None
    parent_id: UUID | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SourceCreate(BaseModel):
    category_id: UUID
    name: str = Field(..., min_length=1, max_length=512, description="Primary business name / lookup key")
    description: str | None = None
    citation_name: str | None = Field(
        default=None,
        description="Short cite label for indexing + chamber footnotes; defaults to name",
    )
    citation_desc: str | None = Field(
        default=None,
        description="How this source should be described when cited after retrieval",
    )
    source_key: str = Field(..., min_length=1, max_length=256)
    url: str | None = None
    license: str | None = None
    status: str = "active"
    meta: dict[str, Any] = Field(default_factory=dict)


class SourceUpdate(BaseModel):
    category_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=512)
    description: str | None = None
    citation_name: str | None = None
    citation_desc: str | None = None
    url: str | None = None
    license: str | None = None
    status: str | None = None
    meta: dict[str, Any] | None = None


class SourceOut(BaseModel):
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
    meta: dict[str, Any]
    created_at: datetime | None = None
    updated_at: datetime | None = None
