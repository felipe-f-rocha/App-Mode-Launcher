import json
import platform
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


CACHE_PATH = Path(__file__).resolve().parents[1] / "config" / "detection_cache.json"
CACHE_TTL = timedelta(hours=6)


def _normalize_candidate(candidate: str) -> str:
    if "{home}" in candidate:
        candidate = candidate.replace("{home}", str(Path.home()))
    return candidate


def _load_detection_cache() -> Dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}

    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        logger.debug("Failed to load detection cache: %s", exc)
        return {}


def _save_detection_cache(os_name: str, installed: Dict[str, str]) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "os_name": os_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "installed": installed,
        }
        with open(CACHE_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
    except Exception as exc:
        logger.debug("Failed to save detection cache: %s", exc)


def _cache_is_valid(cache: Dict[str, Any], os_name: str) -> bool:
    if cache.get("os_name") != os_name:
        return False
    timestamp = cache.get("timestamp")
    if not isinstance(timestamp, str):
        return False
    try:
        cached_at = datetime.fromisoformat(timestamp)
        if cached_at.tzinfo is None:
            cached_at = cached_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - cached_at < CACHE_TTL
    except ValueError:
        return False


def _resolve_path(candidate: str) -> Optional[str]:
    candidate_path = Path(candidate).expanduser()
    if candidate_path.exists() and candidate_path.is_file():
        return str(candidate_path)
    return None


def _resolve_versioned_path(candidate: str) -> Optional[str]:
    if "{version}" not in candidate:
        return None

    normalized = _normalize_candidate(candidate)
    pattern = normalized.replace("{version}", "*")
    path_pattern = Path(pattern)
    parent_dir = path_pattern.parent.parent
    if not parent_dir.exists():
        return None

    for candidate_dir in parent_dir.glob(path_pattern.parent.name):
        resolved_path = candidate_dir / path_pattern.name
        if resolved_path.exists() and resolved_path.is_file():
            return str(resolved_path)

    return None


def _resolve_windows_shortcut(link_path: Path) -> Optional[Dict[str, str]]:
    try:
        escaped_path = str(link_path).replace("'", "''")
        result = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"$sc = (New-Object -ComObject WScript.Shell).CreateShortcut('{escaped_path}'); $sc.TargetPath; $sc.Arguments",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            return None
        return {"target": lines[0], "arguments": " ".join(lines[1:])}
    except Exception as exc:
        logger.debug("Failed to inspect shortcut %s: %s", link_path, exc)
        return None


WINDOWS_SHORTCUT_APP_MAP = {
    "code.exe": "Visual Studio Code",
    "discord.exe": "Discord",
    "slack.exe": "Slack",
    "spotify.exe": "Spotify",
    "steam.exe": "Steam",
    "msedge.exe": "Microsoft Edge",
    "chrome.exe": "Google Chrome",
}


def _scan_windows_shortcuts() -> Dict[str, Dict[str, str]]:
    shortcuts: Dict[str, Dict[str, str]] = {}
    if get_os() != "Windows":
        return shortcuts

    start_menu_paths = [
        Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs",
        Path("C:/ProgramData/Microsoft/Windows/Start Menu/Programs"),
    ]

    for start_menu_path in start_menu_paths:
        if not start_menu_path.exists():
            continue

        for link_path in start_menu_path.rglob("*.lnk"):
            shortcut = _resolve_windows_shortcut(link_path)
            if not shortcut:
                continue

            shortcuts[link_path.stem] = {
                "target": shortcut["target"],
                "arguments": shortcut["arguments"],
            }

    return shortcuts


def _resolve_windows_shortcut_app_name(
    target: str, arguments: str, shortcut_name: str
) -> Optional[Tuple[str, str]]:
    target_path = Path(target)
    app_executable = target_path.name.lower()

    if app_executable == "chrome.exe":
        lower_args = arguments.lower()
        if "--app-id" in lower_args or "--app=" in lower_args:
            return shortcut_name, f"{target} {arguments}".strip()
        return ("Google Chrome", target)

    mapped_name = WINDOWS_SHORTCUT_APP_MAP.get(app_executable)
    if mapped_name:
        return (mapped_name, target)

    return None


def _resolve_candidate(candidate: str) -> Optional[str]:
    normalized = _normalize_candidate(candidate)

    if "{version}" in candidate:
        location = _resolve_versioned_path(candidate)
        if location:
            return location

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


def detect_installed_apps(force_refresh: bool = False) -> Dict[str, str]:
    installed: Dict[str, str] = {}
    os_name = get_os()
    logger.debug("detect_installed_apps called on %s (force_refresh=%s)", os_name, force_refresh)

    if not force_refresh:
        cache = _load_detection_cache()
        if _cache_is_valid(cache, os_name):
            installed = cache.get("installed", {})
            logger.info(
                "Loaded app detection from cache: %s", list(installed.keys())
            )
            return installed

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

        shortcut_entries = _scan_windows_shortcuts()
        for shortcut_name, shortcut_data in shortcut_entries.items():
            resolved = _resolve_windows_shortcut_app_name(
                shortcut_data["target"],
                shortcut_data["arguments"],
                shortcut_name,
            )
            if not resolved:
                continue

            app_name, app_path = resolved
            if app_name not in installed:
                installed[app_name] = app_path
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

    _save_detection_cache(os_name, installed)
    logger.info("Apps detectados: %s", list(installed.keys()))
    return installed


def detect_installed_app_names() -> List[str]:
    return list(detect_installed_apps().keys())
