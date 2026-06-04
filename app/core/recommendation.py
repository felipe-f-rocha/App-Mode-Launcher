from typing import Any, Dict, List, Optional, Tuple

from app.core.analytics import AnalyticsStore


def _normalize_target(target: Any) -> str:
    if target is None:
        return ""
    return str(target).strip().lower()


def _workspace_app_names(workspace: Dict[str, Any]) -> List[str]:
    apps = workspace.get("apps", [])
    if not isinstance(apps, list):
        return []
    return [_normalize_target(app) for app in apps if _normalize_target(app)]


def _app_match_score(workspace: Dict[str, Any], detected_apps: List[str]) -> int:
    detected = {
        _normalize_target(app) for app in detected_apps if _normalize_target(app)
    }
    if not detected:
        return 0

    matches = 0
    for target in _workspace_app_names(workspace):
        if target and any(
            target in detected_app or detected_app in target
            for detected_app in detected
        ):
            matches += 1
    return matches


def _most_common_combo(
    histories: List[List[str]], min_count: int = 2
) -> Optional[List[str]]:
    combo_counts: Dict[Tuple[str, ...], int] = {}
    for detected in histories:
        normalized = tuple(
            sorted(
                {_normalize_target(app) for app in detected if _normalize_target(app)}
            )
        )
        if len(normalized) < 2:
            continue
        combo_counts[normalized] = combo_counts.get(normalized, 0) + 1

    if not combo_counts:
        return None

    top_combo, count = max(combo_counts.items(), key=lambda item: item[1])
    if count < min_count:
        return None

    return list(top_combo)


def recommend_workspace(
    workspaces: List[Dict[str, Any]],
    detected_apps: List[str],
    analytics: AnalyticsStore,
) -> str:
    if not detected_apps:
        return "No recommendation available without app detection."

    scores = {
        workspace.get("name", "unknown"): _app_match_score(workspace, detected_apps)
        for workspace in workspaces
    }

    best_workspace = max(scores, key=scores.get)
    best_score = scores[best_workspace]
    top_workspace_count = analytics.get_workspace_launch_count(best_workspace)
    frequent_combo = analytics.get_frequent_detection_combo()
    normalized_detected = {
        _normalize_target(app) for app in detected_apps if _normalize_target(app)
    }

    if best_score > 0:
        recommendation = (
            f"Recommended workspace: {best_workspace}. It matches the detected apps."
        )
        if top_workspace_count > 0:
            recommendation += (
                f" You have opened it {top_workspace_count} time(s) before."
            )
        if best_score == 1 and frequent_combo:
            overlap = len(set(frequent_combo) & normalized_detected)
            if overlap >= 2:
                recommendation += f' You often use {", ".join(frequent_combo)} together; consider creating a custom workspace for this combo.'
        return recommendation

    if frequent_combo and set(frequent_combo).issubset(normalized_detected):
        suggestion = ", ".join(frequent_combo)
        return f"You often open {suggestion} together. Consider creating a custom workspace for this app group."

    top_workspace = analytics.get_top_workspace()
    if top_workspace:
        return f"No workspace matches the detected apps. Your most-used workspace is {top_workspace}."

    return "No workspace matches the detected apps."
