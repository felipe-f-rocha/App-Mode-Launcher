import platform
import shutil
import subprocess
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
    if "{home}" in candidate:
        candidate = candidate.replace("{home}", str(Path.home()))
    return candidate


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


def _scan_windows_shortcuts_for_chrome_apps() -> Dict[str, str]:
    shortcuts: Dict[str, str] = {}
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

            target = shortcut["target"].lower()
            arguments = shortcut["arguments"].lower()
            if "chrome.exe" in target and ("--app-id" in arguments or "--app=" in arguments):
                shortcuts[link_path.stem] = f"{shortcut['target']} {shortcut['arguments']}".strip()

    return shortcuts


def _search_common_windows_paths(executable_name: str) -> Optional[str]:
    common_dirs = [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path.home() / "AppData" / "Local",
        Path.home() / "AppData" / "Roaming",
    ]
    if not executable_name.lower().endswith(".exe"):
        executable_name = executable_name + ".exe"

    for base_dir in common_dirs:
        if not base_dir.exists():
            continue
        for path in base_dir.rglob(executable_name):
            if path.is_file():
                return str(path)

    return None


def _search_common_non_windows_paths(executable_name: str) -> Optional[str]:
    common_dirs = [Path("/usr/bin"), Path("/usr/local/bin"), Path("/snap/bin")]
    for base_dir in common_dirs:
        if not base_dir.exists():
            continue
        for path in base_dir.rglob(executable_name):
            if path.is_file():
                return str(path)

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

    executable_name = Path(normalized).name
    if get_os() == "Windows":
        return _search_common_windows_paths(executable_name)
    return _search_common_non_windows_paths(executable_name)


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

        chrome_shortcuts = _scan_windows_shortcuts_for_chrome_apps()
        for shortcut_name, shortcut_target in chrome_shortcuts.items():
            if shortcut_name not in installed:
                installed[shortcut_name] = shortcut_target
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
