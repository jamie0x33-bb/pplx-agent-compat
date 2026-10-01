import io
import json

import pytest

from sandbox_compat import cli, registry

PAYLOAD = {"runtime": "computer/2026.09", "python": "3.14.0", "kernel": "6.1.155+"}


def test_submit_without_token_raises(monkeypatch):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    with pytest.raises(registry.NoWorkspaceToken):
        registry.submit(PAYLOAD)


def test_cli_submit_without_token_exits_2(monkeypatch, capsys):
    monkeypatch.delenv("PPLX_AGENT_PROXY_TOKEN", raising=False)
    assert cli.main(["report", "--submit"]) == 2
    assert "workspace bearer" in capsys.readouterr().err


def test_submit_sends_bearer_and_json_body(monkeypatch):
    """The bearer authenticates the request; it is never part of the payload."""
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_fixture")
    seen = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"accepted":true,"workspace":"ws_abc123","entry_id":"mx_0001"}'

    def fake_urlopen(req, timeout=None):
        seen["url"] = req.full_url
        seen["headers"] = {k.lower(): v for k, v in req.header_items()}
        seen["body"] = json.loads(req.data.decode())
        return FakeResponse()

    monkeypatch.setattr(registry.urllib.request, "urlopen", fake_urlopen)
    result = registry.submit(PAYLOAD)

    assert seen["url"].endswith("/api/report")
    assert seen["headers"]["authorization"] == "Bearer agp_fixture"
    assert seen["body"] == PAYLOAD
    assert "agp_fixture" not in json.dumps(seen["body"])
    assert result["workspace"] == "ws_abc123"


class _Body(io.BytesIO):
    """Minimal stand-in for the file object HTTPError carries."""


def test_rejected_surfaces_detail(monkeypatch):
    import urllib.error

    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_fixture")

    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 401, "Unauthorized", {}, _Body(b'{"detail":"nope"}')
        )

    monkeypatch.setattr(registry.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(registry.RegistryRejected) as exc:
        registry.submit(PAYLOAD)
    assert exc.value.status == 401
