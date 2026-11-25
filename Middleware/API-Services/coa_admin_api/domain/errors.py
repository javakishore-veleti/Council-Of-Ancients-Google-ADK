from __future__ import annotations


class AdminError(Exception):
    """Base admin API error."""


class NotFoundError(AdminError):
    pass


class ConflictError(AdminError):
    pass


class ValidationError(AdminError):
    pass
