from __future__ import annotations


class KnowledgeError(Exception):
    """Base knowledge-bank error."""


class NotFoundError(KnowledgeError):
    pass


class ConflictError(KnowledgeError):
    pass


class ValidationError(KnowledgeError):
    pass
