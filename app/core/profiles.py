from typing import Dict, Any, List
import copy
import json
from pathlib import Path

from app.core.logger import logger
from app.plugins import load_plugin_workspaces

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / "config.json"

DEFAULT_CONFIG = {
    "settings": {
        "theme": "dark",
        "startup": {
            "auto_launch": False,
            "workspace_name": "",
            "resume_last_workspace": False,
            "last_workspace": "",
        },
    },
    "apps": {
        "coding": ["YOUR_CODING_APP_PATH_OR_COMMAND", "code"],
        "designing": ["YOUR_DESIGN_APP_PATH_OR_COMMAND", "code"],
        "talking": {"aumid": "PUT_YOUR_TALKING_APP_AUMID_HERE"},
    },
    "workspaces": [
        {"name": "Coding", "type": "apps", "apps": ["code"]},
        {
            "name": "Designing",
            "type": "apps",
            "apps": ["YOUR_DESIGN_APP_PATH_OR_COMMAND"],
        },
        {
            "name": "Talking",
            "type": "talking",
            "aumid": "PUT_YOUR_TALKING_APP_AUMID_HERE",
        },
    ],
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def load_profiles() -> Dict[str, Any]:
    """Load app profiles from config.json."""
    try:
        logger.debug("Attempting to load configuration from %s", CONFIG_PATH)
        if not CONFIG_PATH.exists():
            logger.warning("Configuration not found, using DEFAULT_CONFIG")
            return copy.deepcopy(DEFAULT_CONFIG)

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            logger.error("Invalid configuration format: %s", type(data))
            return copy.deepcopy(DEFAULT_CONFIG)

        merged = copy.deepcopy(DEFAULT_CONFIG)
        merged = _deep_merge(merged, data)
        logger.info("Configuration loaded successfully")
        return merged
    except json.JSONDecodeError as exc:
        logger.exception("Invalid JSON in config.json: %s", exc)
        return copy.deepcopy(DEFAULT_CONFIG)
    except Exception as exc:
        logger.exception("Error loading config.json: %s", exc)
        return copy.deepcopy(DEFAULT_CONFIG)


def save_profiles(config: Dict[str, Any]) -> None:
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        logger.info("Configuration saved to %s", CONFIG_PATH)
    except Exception as exc:
        logger.exception("Failed to save configuration: %s", exc)


def get_workspaces(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(config.get("workspaces"), list):
        base_workspaces = config["workspaces"]
    else:
        apps = config.get("apps", {})
        base_workspaces = [
            {"name": "Coding", "type": "apps", "apps": apps.get("coding", [])},
            {"name": "Designing", "type": "apps", "apps": apps.get("designing", [])},
            {
                "name": "Talking",
                "type": "talking",
                "aumid": apps.get("talking", {}).get("aumid"),
            },
        ]

    plugin_workspaces = load_plugin_workspaces(config)
    return base_workspaces + plugin_workspaces
