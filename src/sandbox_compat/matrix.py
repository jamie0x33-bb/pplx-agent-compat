"""Read side of the compatibility matrix."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .config import DEFAULT_BASE_URL, USER_AGENT

STATUS_ORDER = {"pass": 0, "partial": 1, "fail": 2, "unknown": 3}


class MatrixError(RuntimeError):
    pass


def fetch(base_url: str = DEFAULT_BASE_URL, timeout: float = 10.0) -> dict:
    """Fetch the published matrix. Reads are public and need no credential."""
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/matrix",
        headers={"accept": "application/json", "user-agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise MatrixError(f"could not reach the matrix: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MatrixError(f"matrix response was not JSON: {exc}") from exc


def entry_for(matrix: dict, runtime: str) -> dict | None:
    for entry in matrix.get("entries", []):
        if entry.get("runtime") == runtime:
            return entry
    return None


def summarise(matrix: dict) -> list[dict]:
    entries = list(matrix.get("entries", []))
    entries.sort(key=lambda e: STATUS_ORDER.get(e.get("status", "unknown"), 9))
    return entries
