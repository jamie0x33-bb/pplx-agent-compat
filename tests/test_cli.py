import json

from pplx_agent_compat import cli


def test_probe_json(capsys):
    assert cli.main(["probe", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert {"runtime", "python", "kernel"} <= payload.keys()


def test_probe_table(capsys):
    assert cli.main(["probe"]) == 0
    assert "runtime" in capsys.readouterr().out


def test_report_prints_payload(capsys):
    assert cli.main(["report"]) == 0
    assert "connector_schema" in json.loads(capsys.readouterr().out)


def test_check_reports_missing_runtime(capsys, monkeypatch):
    monkeypatch.setattr(cli.matrix_mod, "fetch", lambda *a, **k: {"entries": []})
    assert cli.main(["check", "mypackage", "--runtime", "computer/2026.09"]) == 0
    assert "no entries recorded" in capsys.readouterr().out


def test_check_reports_status(capsys, monkeypatch):
    monkeypatch.setattr(
        cli.matrix_mod,
        "fetch",
        lambda *a, **k: {
            "entries": [{"runtime": "computer/2026.09", "status": "pass", "entries": 41}]
        },
    )
    assert cli.main(["check", "mypackage", "--runtime", "computer/2026.09"]) == 0
    assert "pass (41 workspaces)" in capsys.readouterr().out
