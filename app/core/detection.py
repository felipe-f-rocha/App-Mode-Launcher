import platform
import shutil
from pathlib import Path
from typing import Dict, Optional, List

from app.core.logger import logger

COMMON_WINDOWS_APPS = {
    "Visual Studio Code": [
        "code.exe",
        "C:/Program Files/Microsoft VS Code/Code.exe",
        "C:/Program Files (x86)/Microsoft VS Code/Code.exe",
        "C:/Users/{home}/AppData/Local/Programs/Microsoft VS Code/Code.exe",
    ],
    "Google Chrome": [
        "chrome.exe",
        "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    ],
    "Discord": ["Discord.exe"],
    "Spotify": ["spotify.exe", "C:/Users/{home}/AppData/Roaming/Spotify/Spotify.exe"],
    "Steam": [
        "steam.exe",
        "C:/Program Files (x86)/Steam/Steam.exe",
        "C:/Program Files/Steam/Steam.exe",
    ],
    "Microsoft Edge": [
        "msedge.exe",
        "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
        "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    ],
    "Slack": [
        "slack.exe",
        "C:/Program Files/Slack/Slack.exe",
        "C:/Users/{home}/AppData/Local/slack/app-{version}/slack.exe",
    ],
}

COMMON_NON_WINDOWS_APPS = {
    "Visual Studio Code": ["code", "code-insiders"],
    "Google Chrome": ["google-chrome", "chrome", "chromium-browser", "chromium"],
    "Firefox": ["firefox"],
    "Spotify": ["spotify"],
    "Steam": ["steam"],
    "Discord": ["discord"],
}

COMMON_MAC_APPS = {
    "Visual Studio Code": ["Visual Studio Code.app"],
    "Google Chrome": ["Google Chrome.app"],
    "Firefox": ["Firefox.app"],
    "Spotify": ["Spotify.app"],
    "Steam": ["Steam.app"],
}


def get_os() -> str:
    return platform.system()


def _normalize_candidate(candidate: str) -> str:
    return candidate.format(home=Path.home())


def _resolve_path(candidate: str) -> Optional[str]:
    candidate_path = Path(candidate).expanduser()
    if candidate_path.exists() and candidate_path.is_file():
        return str(candidate_path)
    return None


def _resolve_candidate(candidate: str) -> Optional[str]:
    normalized = _normalize_candidate(candidate)

    if Path(normalized).is_absolute():
        return _resolve_path(normalized)

    location = shutil.which(normalized)
    if location:
        return location

    return None


def _resolve_discord() -> Optional[str]:
    if get_os() != "Windows":
        return None

    discord_base = Path.home() / "AppData" / "Local" / "Discord"
    if discord_base.exists():
        for exe in discord_base.rglob("Discord.exe"):
            if exe.is_file():
                return str(exe)
    return None


def _detect_mac_app(bundle_name: str) -> Optional[str]:
    apps_dir = Path("/Applications")
    candidate = apps_dir / bundle_name
    if candidate.exists():
        return str(candidate)
    return None


def detect_installed_apps() -> Dict[str, str]:
    installed: Dict[str, str] = {}
    os_name = get_os()
    logger.debug("detect_installed_apps called on %s", os_name)

    if os_name == "Windows":
        for app_name, candidates in COMMON_WINDOWS_APPS.items():
            for candidate in candidates:
                if app_name == "Discord":
                    location = _resolve_discord()
                else:
                    location = _resolve_candidate(candidate)
                if location:
                    installed[app_name] = location
                    break
    elif os_name == "Darwin":
        for app_name, candidates in COMMON_MAC_APPS.items():
            for candidate in candidates:
                location = _detect_mac_app(candidate)
                if location:
                    installed[app_name] = location
                    break
    else:
        for app_name, candidates in COMMON_NON_WINDOWS_APPS.items():
            for candidate in candidates:
                location = _resolve_candidate(candidate)
                if location:
                    installed[app_name] = location
                    break

    logger.info("Apps detectados: %s", list(installed.keys()))
    return installed


def detect_installed_app_names() -> List[str]:
    return list(detect_installed_apps().keys())
