import shutil
from pathlib import Path

from app.core.detection import _resolve_candidate, detect_installed_apps


def test_resolve_candidate_finds_command(monkeypatch):
    monkeypatch.setattr(
        shutil, "which", lambda x: "/usr/bin/code" if x == "code" else None
    )
    assert _resolve_candidate("code") == "/usr/bin/code"


def test_resolve_candidate_path(monkeypatch, tmp_path):
    candidate = tmp_path / "app.exe"
    candidate.write_text("")
    assert _resolve_candidate(str(candidate)) == str(candidate)


def test_detect_installed_apps_returns_dict(monkeypatch):
    monkeypatch.setattr("app.core.detection.get_os", lambda: "Linux")
    monkeypatch.setattr(
        shutil, "which", lambda x: "/usr/bin/code" if x == "code" else None
    )
    apps = detect_installed_apps()
    assert isinstance(apps, dict)
    assert "Visual Studio Code" in apps
