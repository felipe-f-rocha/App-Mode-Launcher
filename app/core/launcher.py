import subprocess
import webbrowser
from typing import List, Dict, Any

from app.core.analytics import AnalyticsStore
from app.core.logger import logger
from app.plugins import notify_workspace_launched


def launch_apps(apps: List[str]) -> None:
    """Launch a list of applications."""
    logger.debug("launch_apps called with apps=%s", apps)
    for app in apps:
        if isinstance(app, str) and app.strip():
            subprocess.Popen(app, shell=True)
            logger.info("Command sent to launch app: %s", app)


def open_websites(urls: List[str]) -> None:
    """Open a list of URLs in the default browser."""
    logger.debug("open_websites called with urls=%s", urls)
    for url in urls:
        if isinstance(url, str) and url.strip():
            webbrowser.open_new_tab(url)
            logger.info("Website opened: %s", url)


def launch_talking(aumid: str) -> None:
    """Launch a talking app using Microsoft Store AUMID."""
    logger.debug("launch_talking called with aumid=%s", aumid)
    if not aumid:
        logger.warning("Missing AUMID when attempting to launch talking workspace")
        return

    subprocess.Popen(["explorer.exe", f"shell:appsFolder\\{aumid}"])
    logger.info("Talking workspace launched with AUMID: %s", aumid)


def launch_workspace(workspace: Dict[str, Any]) -> None:
    """Launch a workspace from configuration definition."""
    logger.debug("launch_workspace called with workspace=%s", workspace)
    if not isinstance(workspace, dict):
        logger.error("Invalid workspace: %s", workspace)
        return

    apps: List[str] = (
        workspace.get("apps", []) if isinstance(workspace.get("apps", []), list) else []
    )
    websites: List[str] = (
        workspace.get("websites", [])
        if isinstance(workspace.get("websites", []), list)
        else []
    )

    if workspace.get("type") == "talking":
        launch_talking(workspace.get("aumid", ""))
        AnalyticsStore.load().track_workspace_launch(workspace.get("name", "unknown"))
        notify_workspace_launched(workspace)
        return

    if apps:
        launch_apps(apps)

    if websites:
        open_websites(websites)

    AnalyticsStore.load().track_workspace_launch(
        workspace.get("name", "unknown"), apps, websites
    )
    notify_workspace_launched(workspace)
