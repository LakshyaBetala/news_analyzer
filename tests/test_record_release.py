import json
import subprocess
import sys


def test_only_real_gate_failures_are_recorded_as_blocked(tmp_path, monkeypatch):
    from scripts import record_release
    monkeypatch.chdir(tmp_path)
    ev = tmp_path / "ev.json"
    for status, passed, expect in [("BLOCKED", True, 0), ("BLOCKED", False, 1), ("PROMOTED", True, 2)]:
        ev.write_text(json.dumps({"accuracy": 1.0, "passed": passed, "reasons": [] if passed else ["too low"]}))
        monkeypatch.setattr(sys, "argv", ["x", "--version", "1.x", "--status", status, "--eval", str(ev)])
        record_release.main()
        rows = json.loads((tmp_path / "releases.json").read_text()) if (tmp_path / "releases.json").exists() else []
        assert len(rows) == expect
