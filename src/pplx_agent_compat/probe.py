"""Collect a runtime fingerprint for the compatibility matrix."""

from __future__ import annotations

import os
import platform
import sys
from dataclasses import asdict, dataclass, field
from importlib import metadata
from pathlib import Path

CONNECTOR_SCHEMA_BY_IMAGE = {
    "computer/2026.09": "v3",
    "computer/2026.08": "v3",
    "computer/2026.07": "v2",
    "computer/2026.06": "v1",
}

TRACKED_PACKAGES = ("pplx-agent-compat", "httpx", "requests")


def detect_runtime() -> str:
    """Identify the sandbox image.

    Computer sandboxes advertise their type in SANDBOX_TYPE and, on tagged
    images, the tag in SANDBOX_IMAGE_TAG. Untagged images are reported as
    unknown and are excluded from the aggregate matrix.
    """
    if not os.environ.get("SANDBOX_TYPE"):
        return "local"
    tag = os.environ.get("SANDBOX_IMAGE_TAG", "").strip()
    return f"computer/{tag}" if tag else "computer/unknown"


def cache_root() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    return Path(base) / "pplx-agent-compat"


def tracked_versions() -> dict[str, str]:
    found = {}
    for name in TRACKED_PACKAGES:
        try:
            found[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return found


@dataclass
class Fingerprint:
    runtime: str
    python: str
    kernel: str
    connector_schema: str
    cache_root: str
    packages: dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)

    def rows(self) -> list[tuple[str, str]]:
        return [
            ("runtime", self.runtime),
            ("python", self.python),
            ("kernel", self.kernel),
            ("connector_schema", self.connector_schema),
            ("cache_root", self.cache_root),
        ]


def collect() -> Fingerprint:
    runtime = detect_runtime()
    return Fingerprint(
        runtime=runtime,
        python="{}.{}.{}".format(*sys.version_info[:3]),
        kernel=platform.release(),
        connector_schema=CONNECTOR_SCHEMA_BY_IMAGE.get(runtime, "unknown"),
        cache_root=str(cache_root()),
        packages=tracked_versions(),
    )
