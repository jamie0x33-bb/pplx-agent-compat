import json

from pplx_agent_compat import probe


def test_detect_runtime_local_outside_sandbox(monkeypatch):
    monkeypatch.delenv("SANDBOX_TYPE", raising=False)
    assert probe.detect_runtime() == "local"


def test_detect_runtime_tagged(monkeypatch):
    monkeypatch.setenv("SANDBOX_TYPE", "asi_session")
    monkeypatch.setenv("SANDBOX_IMAGE_TAG", "2026.09")
    assert probe.detect_runtime() == "computer/2026.09"


def test_detect_runtime_untagged_is_unknown(monkeypatch):
    monkeypatch.setenv("SANDBOX_TYPE", "asi_session")
    monkeypatch.delenv("SANDBOX_IMAGE_TAG", raising=False)
    assert probe.detect_runtime() == "computer/unknown"


def test_collect_is_json_serialisable():
    fp = probe.collect()
    payload = json.dumps(fp.as_dict())
    assert json.loads(payload)["python"].count(".") == 2


def test_fingerprint_carries_no_token(monkeypatch):
    """The fingerprint must never carry a credential."""
    monkeypatch.setenv("PPLX_AGENT_PROXY_TOKEN", "agp_should_not_appear")
    blob = json.dumps(probe.collect().as_dict())
    assert "agp_should_not_appear" not in blob


def test_connector_schema_resolves_for_known_image(monkeypatch):
    monkeypatch.setenv("SANDBOX_TYPE", "asi_session")
    monkeypatch.setenv("SANDBOX_IMAGE_TAG", "2026.06")
    assert probe.collect().connector_schema == "v1"


def test_cache_root_honours_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
    assert probe.cache_root() == tmp_path / "pplx-agent-compat"
