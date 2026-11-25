from __future__ import annotations

import os
from pathlib import Path


def kb_root() -> Path:
    """Blob root outside the public git clone when possible.

    Default App Endpoint path:
      $HOME/runtime_data/apps/datasets/COA/KnowledgeBase/
    Override with KB_LOCAL_ROOT. Subfolders must use no spaces.
    """
    raw = os.environ.get("KB_LOCAL_ROOT", "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return (Path.home() / "runtime_data/apps/datasets/COA/KnowledgeBase").resolve()


def _slug(part: str) -> str:
    """Folder segment with no spaces (and no path separators)."""
    return (
        part.strip()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )


def source_store_dir(category_code: str, subcategory_code: str, source_id: str) -> Path:
    """Downloaded files for one source under the KnowledgeBase endpoint.

    Leaf is the source UUID — not a semantic source_key — so paths stay unique at 100k+.
    """
    return kb_root() / _slug(category_code) / _slug(subcategory_code) / _slug(source_id)


def topic_raw(topic_id: str, source_id: str) -> Path:
    return kb_root() / "raw" / _slug(topic_id) / _slug(source_id)


def topic_text(topic_id: str, source_id: str) -> Path:
    return kb_root() / "text" / _slug(topic_id) / _slug(source_id)


def topic_derived(topic_id: str, source_id: str) -> Path:
    return kb_root() / "derived" / _slug(topic_id) / _slug(source_id)


def chroma_path() -> Path:
    return kb_root() / "vector" / "chroma"
