import pytest

from pplx_agent_compat import matrix

SAMPLE = {
    "revision": "2026-09-29",
    "entries": [
        {"runtime": "computer/2026.06", "status": "fail", "entries": 18},
        {"runtime": "computer/2026.09", "status": "pass", "entries": 41},
        {"runtime": "computer/2026.07", "status": "partial", "entries": 73},
    ],
}


def test_entry_for_found():
    assert matrix.entry_for(SAMPLE, "computer/2026.09")["status"] == "pass"


def test_entry_for_missing_returns_none():
    assert matrix.entry_for(SAMPLE, "computer/1999.01") is None


def test_summarise_orders_pass_first():
    order = [e["status"] for e in matrix.summarise(SAMPLE)]
    assert order == ["pass", "partial", "fail"]


def test_fetch_wraps_network_error(monkeypatch):
    import urllib.error

    def boom(*a, **k):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(matrix.urllib.request, "urlopen", boom)
    with pytest.raises(matrix.MatrixError):
        matrix.fetch("https://example.invalid")
