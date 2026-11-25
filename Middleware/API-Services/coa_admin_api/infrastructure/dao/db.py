from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg.rows import dict_row


def database_url() -> str:
    return os.getenv(
        "COA_ADMIN_DATABASE_URL",
        os.getenv(
            "COA_KNOWLEDGE_DATABASE_URL",
            os.getenv(
                "DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/council",
            ),
        ),
    )


@contextmanager
def connection() -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(database_url(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
