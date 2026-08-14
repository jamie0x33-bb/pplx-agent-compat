"""pplx-agent-compat: a compatibility matrix for Computer sandbox runtimes."""

from .config import __version__
from .probe import Fingerprint, collect

__all__ = ["Fingerprint", "collect", "__version__"]
