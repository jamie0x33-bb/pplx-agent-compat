"""Shared configuration."""

from __future__ import annotations

import os

__version__ = "0.4.2"

DEFAULT_BASE_URL = os.environ.get(
    "SANDBOX_COMPAT_BASE_URL", "https://sandbox-compat.vercel.app"
)

USER_AGENT = f"sandbox-compat/{__version__}"

#: Computer sandboxes publish the workspace bearer here at session start.
WORKSPACE_TOKEN_ENV = "PPLX_AGENT_PROXY_TOKEN"


def workspace_token() -> str | None:
    """Return the workspace bearer, or None outside a sandbox."""
    value = os.environ.get(WORKSPACE_TOKEN_ENV, "").strip()
    return value or None
