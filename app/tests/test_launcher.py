import subprocess

from app.core.launcher import launch_apps, launch_workspace


def test_launch_apps_calls_subprocess(monkeypatch):
    calls = []

    def fake_popen(cmd, shell):
        calls.append((cmd, shell))

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    launch_apps(["code", "python"])

    assert calls == [("code", True), ("python", True)]


def test_launch_workspace_apps(monkeypatch):
    calls = []

    def fake_popen(cmd, shell):
        calls.append((cmd, shell))

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    workspace = {"type": "apps", "apps": ["code"]}
    launch_workspace(workspace)
    assert calls == [("code", True)]


def test_launch_workspace_talking(monkeypatch):
    calls = []

    def fake_popen(cmd, shell=None):
        calls.append((cmd, shell))

    monkeypatch.setattr(subprocess, "Popen", fake_popen)
    workspace = {"type": "talking", "aumid": "test"}
    launch_workspace(workspace)
    assert calls == [(["explorer.exe", "shell:appsFolder\\test"], None)]
