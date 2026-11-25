from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AppEndpointOut(BaseModel):
    id: UUID
    name: str
    kind: str
    provider: str
    endpoint_url: str
    resource: str
    region: str | None = None
    status: str
    notes: str | None = None
    created_on: datetime | None = Field(default=None, validation_alias="created_at")
    updated_on: datetime | None = Field(default=None, validation_alias="updated_at")

    model_config = {"from_attributes": True, "populate_by_name": True}


class AdminSourceOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    citation_name: str
    citation_desc: str | None = None
    category_name: str
    category_code: str
    subcategory_name: str
    subcategory_code: str
    url: str | None = None
    license: str | None = None
    ingest_status: str
    created_on: datetime | None = None
    updated_on: datetime | None = None
    download_from_endpoint_id: UUID | None = None
    store_to_endpoint_ids: list[UUID] = Field(default_factory=list)
    tech_stack_endpoint_ids: list[UUID] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class WfExecLogOut(BaseModel):
    id: UUID
    source_id: UUID
    engine: str
    external_run_id: str | None = None
    status: str
    download_from_endpoint_id: UUID | None = None
    store_to_endpoint_ids: list[UUID] = Field(default_factory=list)
    tech_stack_endpoint_ids: list[UUID] = Field(default_factory=list)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_on: datetime
    updated_on: datetime
    error_message: str | None = None
    detail: str | None = None

    model_config = {"from_attributes": True}


class DownloadJobOut(BaseModel):
    wf_exec_log_id: UUID
    source_id: UUID
    status: Literal["queued"] = "queued"
    download_from_endpoint_id: UUID | None = None
    store_to_endpoint_ids: list[UUID] = Field(default_factory=list)


class WfExecLogPatch(BaseModel):
    status: str | None = None
    external_run_id: str | None = None
    error_message: str | None = None
    detail: str | None = None
