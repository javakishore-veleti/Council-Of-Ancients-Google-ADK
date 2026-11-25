from __future__ import annotations

ALLOWED = {
    "CC-BY-SA-4.0",
    "CC-BY-4.0",
    "CC-BY-NC-SA-4.0",
    "CC-BY-NC-4.0",
    "CC0-1.0",
    "US-Government-Work",
    "public-domain",
}

DENIED_MARKERS = ("ARR", "all-rights-reserved", "unknown", "")


def allowed(license_id: str | None) -> bool:
    if not license_id:
        return False
    key = license_id.strip()
    if key.lower() in DENIED_MARKERS:
        return False
    return key in ALLOWED
