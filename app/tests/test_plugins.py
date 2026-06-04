import json
from pathlib import Path

from app.core.profiles import get_workspaces, load_profiles


def test_plugin_workspaces_are_loaded():
    config = load_profiles()
    workspaces = get_workspaces(config)
    assert any(workspace.get("name") == "Research" for workspace in workspaces)


def test_plugin_module_can_register_workspace():
    config = load_profiles()
    workspaces = get_workspaces(config)
    research_workspace = next(
        (workspace for workspace in workspaces if workspace.get("name") == "Research"),
        None,
    )
    assert research_workspace is not None
    assert research_workspace.get("type") == "apps"
    assert research_workspace.get("apps") == ["firefox"]
