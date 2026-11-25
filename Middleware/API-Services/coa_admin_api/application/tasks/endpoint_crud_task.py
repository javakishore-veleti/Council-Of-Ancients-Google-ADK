from __future__ import annotations

from uuid import UUID

from coa_admin_api.application.sub_facades.endpoint_sub_facade import EndpointSubFacade
from coa_admin_api.application.tasks.base import BaseAdminTask
from coa_admin_api.domain.models import AppEndpoint


class EndpointCrudTask(BaseAdminTask):
    name = "endpoint_crud"

    def __init__(self, sub: EndpointSubFacade | None = None) -> None:
        self._sub = sub or EndpointSubFacade()

    def list(self) -> list[AppEndpoint]:
        return self._sub.list()

    def get(self, endpoint_id: UUID) -> AppEndpoint:
        return self._sub.get(endpoint_id)
