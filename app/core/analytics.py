import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.core.logger import logger

BASE_DIR = Path(__file__).resolve().parents[1]
ANALYTICS_PATH = BASE_DIR / "config" / "analytics.json"

DEFAULT_ANALYTICS: Dict[str, Any] = {
    "workspace_launches": {},
    "recent_launches": [],
    "detection_history": [],
    "total_launches": 0,
    "total_detections": 0,
}


class AnalyticsStore:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self._ensure_defaults()

    def _ensure_defaults(self) -> None:
        for key, value in DEFAULT_ANALYTICS.items():
            self.data.setdefault(key, value)

    @classmethod
    def load(cls) -> "AnalyticsStore":
        if not ANALYTICS_PATH.exists():
            return cls(DEFAULT_ANALYTICS.copy())

        try:
            with open(ANALYTICS_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
            if not isinstance(data, dict):
                logger.warning(
                    "Invalid analytics file format, resetting analytics data"
                )
                return cls(DEFAULT_ANALYTICS.copy())
            return cls(data)
        except json.JSONDecodeError as exc:
            logger.exception("Invalid JSON in analytics file: %s", exc)
            return cls(DEFAULT_ANALYTICS.copy())
        except Exception as exc:
            logger.exception("Error loading analytics file: %s", exc)
            return cls(DEFAULT_ANALYTICS.copy())

    def save(self) -> None:
        ANALYTICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(ANALYTICS_PATH, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=2)

    def track_workspace_launch(
        self, workspace_name: str, apps: List[str] = None, websites: List[str] = None
    ) -> None:
        workspace_name = workspace_name or "unknown"
        self.data["workspace_launches"][workspace_name] = (
            self.data["workspace_launches"].get(workspace_name, 0) + 1
        )
        self.data["total_launches"] += 1
        self.data["recent_launches"].insert(
            0,
            {
                "workspace": workspace_name,
                "apps": apps or [],
                "websites": websites or [],
            },
        )
        self.data["recent_launches"] = self.data["recent_launches"][:5]
        self.save()
        logger.info("Analytics tracked workspace launch: %s", workspace_name)

    def track_detection(self, detected_apps: List[str]) -> None:
        self.data["total_detections"] += 1
        self.data["detection_history"].insert(0, detected_apps)
        self.data["detection_history"] = self.data["detection_history"][:5]
        self.save()
        logger.info("Analytics tracked app detection: %s", detected_apps)

    def get_top_workspace(self) -> str:
        workspace_launches = self.data.get("workspace_launches", {})
        if not workspace_launches:
            return ""
        return max(workspace_launches, key=workspace_launches.get)

    def get_workspace_launch_count(self, workspace_name: str) -> int:
        return int(self.data.get("workspace_launches", {}).get(workspace_name, 0))

    def get_frequent_detection_combo(self, min_count: int = 2) -> List[str]:
        combo_counts: Dict[Tuple[str, ...], int] = {}
        for detected in self.data.get("detection_history", []):
            if not isinstance(detected, list):
                continue
            normalized = tuple(
                sorted(
                    {
                        str(app).strip().lower()
                        for app in detected
                        if isinstance(app, str) and app.strip()
                    }
                )
            )
            if len(normalized) < 2:
                continue
            combo_counts[normalized] = combo_counts.get(normalized, 0) + 1

        if not combo_counts:
            return []

        top_combo, top_count = max(combo_counts.items(), key=lambda item: item[1])
        if top_count < min_count:
            return []

        return list(top_combo)

    def get_last_workspace(self) -> str:
        if self.data.get("recent_launches"):
            return self.data["recent_launches"][0].get("workspace", "")
        return ""

    def get_total_launches(self) -> int:
        return int(self.data.get("total_launches", 0))

    def get_total_detections(self) -> int:
        return int(self.data.get("total_detections", 0))
