"""Write side of the compatibility matrix.

Submissions are attributed to an opaque workspace identifier derived by the
registry from the workspace bearer. See docs/registry.md for why attribution is
required and what the registry retains.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .config import DEFAULT_BASE_URL, USER_AGENT, WORKSPACE_TOKEN_ENV, workspace_token


class NoWorkspaceToken(RuntimeError):
    """Raised outside a sandbox, where there is nothing to attribute an entry to."""

    def __init__(self) -> None:
        super().__init__(
            f"{WORKSPACE_TOKEN_ENV} is not set; submission needs a workspace bearer"
        )


class RegistryRejected(RuntimeError):
    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"registry returned {status}: {detail}")


def submit(payload: dict, base_url: str = DEFAULT_BASE_URL, timeout: float = 15.0) -> dict:
    """POST a fingerprint to the registry.

    The workspace bearer is read from the environment. It authenticates the
    submission so the entry can be attributed and deduplicated; it is not part
    of the payload.
    """
    token = workspace_token()
    if not token:
        raise NoWorkspaceToken()

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/report",
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "accept": "application/json",
            "authorization": f"Bearer {token}",
            "user-agent": USER_AGENT,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            detail = json.loads(raw).get("detail", raw)
        except json.JSONDecodeError:
            detail = raw
        raise RegistryRejected(exc.code, detail) from exc
    except urllib.error.URLError as exc:
        raise RegistryRejected(0, f"could not reach the registry: {exc}") from exc
