"""Plugin loading framework for App Mode Launcher.

Plugins are discovered from the `app/plugins/` directory and may register
additional workspaces or receive runtime hooks during detection and launch.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.core.logger import logger

PLUGIN_DIR = Path(__file__).resolve().parent
_loaded_plugins: Optional[List[Any]] = None


def _iter_plugin_files() -> List[Path]:
    return [path for path in PLUGIN_DIR.glob("*.py") if path.name != "__init__.py"]


def _load_plugin_module(path: Path) -> Optional[Any]:
    spec = importlib.util.spec_from_file_location(f"app.plugins.{path.stem}", path)
    if not spec or not spec.loader:
        return None

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as exc:
        logger.exception("Failed to load plugin %s: %s", path.name, exc)
        return None


def load_plugins() -> List[Any]:
    global _loaded_plugins
    if _loaded_plugins is not None:
        return _loaded_plugins

    _loaded_plugins = []
    for plugin_path in _iter_plugin_files():
        module = _load_plugin_module(plugin_path)
        if module:
            _loaded_plugins.append(module)
            logger.info("Plugin loaded: %s", plugin_path.name)
    return _loaded_plugins


def load_plugin_workspaces(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    workspaces: List[Dict[str, Any]] = []
    for plugin in load_plugins():
        register = getattr(plugin, "register_workspaces", None)
        if callable(register):
            try:
                result = register(config)
                if isinstance(result, list):
                    workspaces.extend(result)
            except Exception as exc:
                logger.exception("Plugin register_workspaces failed: %s", exc)
    return workspaces


def notify_workspace_launched(workspace: Dict[str, Any]) -> None:
    for plugin in load_plugins():
        callback = getattr(plugin, "on_workspace_launched", None)
        if callable(callback):
            try:
                callback(workspace)
            except Exception as exc:
                logger.exception("Plugin on_workspace_launched failed: %s", exc)


def notify_apps_detected(detected_apps: List[str]) -> None:
    for plugin in load_plugins():
        callback = getattr(plugin, "on_apps_detected", None)
        if callable(callback):
            try:
                callback(detected_apps)
            except Exception as exc:
                logger.exception("Plugin on_apps_detected failed: %s", exc)
