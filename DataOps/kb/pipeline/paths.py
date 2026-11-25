from __future__ import annotations

import os
from pathlib import Path


def kb_root() -> Path:
    """Blob root outside the public git clone when possible."""
    raw = os.environ.get("KB_LOCAL_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    # Default: sibling of the repo so downloads never sit in the public tree.
    repo = Path(__file__).resolve().parents[3]
    return (repo.parent / "council-kb-data").resolve()


def topic_raw(topic_id: str, source_id: str) -> Path:
    return kb_root() / "raw" / topic_id / source_id


def topic_text(topic_id: str, source_id: str) -> Path:
    return kb_root() / "text" / topic_id / source_id


def topic_derived(topic_id: str, source_id: str) -> Path:
    return kb_root() / "derived" / topic_id / source_id


def chroma_path() -> Path:
    return kb_root() / "vector" / "chroma"
