"""Example plugin for App Mode Launcher.

This plugin demonstrates the supported plugin hook functions:
- register_workspaces
- on_workspace_launched
- on_apps_detected
"""

from typing import Dict, Any, List

from app.core.logger import logger


def register_workspaces(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    logger.info("Example plugin: registering extra workspace")
    return [
        {
            "name": "Research",
            "type": "apps",
            "apps": ["firefox"],
            "description": "Open a lightweight research workspace with browser tools.",
        }
    ]


def on_workspace_launched(workspace: Dict[str, Any]) -> None:
    logger.info("Example plugin: workspace launched - %s", workspace.get("name"))


def on_apps_detected(detected_apps: List[str]) -> None:
    logger.info("Example plugin: detected apps - %s", detected_apps)
