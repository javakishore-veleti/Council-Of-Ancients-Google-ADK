from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class AppEndpoint:
    id: UUID
    name: str
    kind: str
    provider: str
    endpoint_url: str
    resource: str
    region: str | None
    status: str
    notes: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class Workflow:
    """Registered ingest/ops workflow (Airflow DAG, Step Functions, EMR, …)."""

    id: UUID
    name: str
    description: str | None
    engine: str
    external_ref: str | None
    status: str
    meta: dict[str, Any] = field(default_factory=dict)
    created_on: datetime | None = None
    updated_on: datetime | None = None


@dataclass
class AdminKnowledgeSource:
    id: UUID
    name: str
    description: str | None
    citation_name: str
    citation_desc: str | None
    category_name: str
    category_code: str
    subcategory_name: str
    subcategory_code: str
    url: str | None
    license: str | None
    ingest_status: str
    created_on: datetime | None
    updated_on: datetime | None
    download_from_endpoint_id: UUID | None
    store_to_endpoint_ids: list[UUID] = field(default_factory=list)
    tech_stack_endpoint_ids: list[UUID] = field(default_factory=list)
    workflow_id: UUID | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class WfExecLog:
    id: UUID
    source_id: UUID
    engine: str
    external_run_id: str | None
    status: str
    download_from_endpoint_id: UUID | None
    store_to_endpoint_ids: list[UUID]
    tech_stack_endpoint_ids: list[UUID]
    started_at: datetime | None
    finished_at: datetime | None
    created_on: datetime
    updated_on: datetime
    wf_id: UUID | None = None
    error_message: str | None = None
    detail: str | None = None
