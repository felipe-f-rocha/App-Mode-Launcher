import json
from pathlib import Path

import pytest

from app.core.profiles import (
    DEFAULT_CONFIG,
    CONFIG_PATH,
    get_workspaces,
    load_profiles,
    save_profiles,
)


def test_load_profiles_returns_default_on_missing(tmp_path, monkeypatch):
    fake_path = tmp_path / "config.json"
    monkeypatch.setattr("app.core.profiles.CONFIG_PATH", fake_path)
    result = load_profiles()
    assert result == DEFAULT_CONFIG


def test_get_workspaces_from_config():
    config = {"workspaces": [{"name": "Test", "type": "apps", "apps": ["code"]}]}
    workspaces = get_workspaces(config)
    assert isinstance(workspaces, list)
    assert workspaces[0]["name"] == "Test"


def test_load_profiles_merges_nested_settings(tmp_path, monkeypatch):
    patched_file = tmp_path / "config.json"
    patched_file.write_text(
        json.dumps({"settings": {"startup": {"auto_launch": True}}})
    )
    monkeypatch.setattr("app.core.profiles.CONFIG_PATH", patched_file)

    result = load_profiles()
    assert result["settings"]["theme"] == "dark"
    assert result["settings"]["startup"]["auto_launch"] is True
    assert result["settings"]["startup"]["workspace_name"] == ""


def test_save_profiles_writes_file(tmp_path, monkeypatch):
    fake_path = tmp_path / "config.json"
    monkeypatch.setattr("app.core.profiles.CONFIG_PATH", fake_path)
    config = load_profiles()
    config["settings"]["startup"]["workspace_name"] = "Coding"

    save_profiles(config)
    saved = json.loads(fake_path.read_text(encoding="utf-8"))
    assert saved["settings"]["startup"]["workspace_name"] == "Coding"


def test_load_profiles_invalid_json(tmp_path, monkeypatch):
    invalid_file = tmp_path / "config.json"
    invalid_file.write_text("{ invalid json }")
    monkeypatch.setattr("app.core.profiles.CONFIG_PATH", invalid_file)

    result = load_profiles()
    assert result == DEFAULT_CONFIG
