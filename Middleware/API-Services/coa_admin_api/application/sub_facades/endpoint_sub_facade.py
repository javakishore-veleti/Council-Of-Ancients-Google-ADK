from __future__ import annotations

from uuid import UUID

from coa_admin_api.domain.models import AppEndpoint
from coa_admin_api.infrastructure.dao.endpoint_dao import EndpointDao


class EndpointSubFacade:
    def __init__(self, dao: EndpointDao | None = None) -> None:
        self._dao = dao or EndpointDao()

    def list(self) -> list[AppEndpoint]:
        return self._dao.list()

    def get(self, endpoint_id: UUID) -> AppEndpoint:
        return self._dao.get(endpoint_id)
