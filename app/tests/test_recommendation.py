import pytest

from app.core.analytics import AnalyticsStore
from app.core.recommendation import recommend_workspace


def test_recommend_workspace_prefers_matching_workspace_with_usage_count():
    workspaces = [
        {"name": "Coding", "type": "apps", "apps": ["code", "python"]},
        {"name": "Designing", "type": "apps", "apps": ["photoshop", "figma"]},
    ]
    analytics = AnalyticsStore(
        {
            "workspace_launches": {"Coding": 3},
            "recent_launches": [],
            "detection_history": [],
        }
    )

    recommendation = recommend_workspace(
        workspaces, ["Visual Studio Code", "Python"], analytics
    )
    assert "Recommended workspace: Coding." in recommendation
    assert "opened it 3 time(s) before" in recommendation


def test_recommend_workspace_suggests_custom_workspace_for_common_combo():
    workspaces = [{"name": "Coding", "type": "apps", "apps": ["code"]}]
    analytics = AnalyticsStore(
        {
            "workspace_launches": {},
            "recent_launches": [],
            "detection_history": [
                ["Visual Studio Code", "Chrome"],
                ["Visual Studio Code", "Chrome"],
                ["Visual Studio Code", "Slack"],
            ],
        }
    )

    recommendation = recommend_workspace(
        workspaces, ["Visual Studio Code", "Chrome", "Slack"], analytics
    )
    assert "consider creating a custom workspace" in recommendation.lower()
    assert "visual studio code" in recommendation.lower()
    assert "chrome" in recommendation.lower()


def test_recommend_workspace_no_match_with_top_workspace():
    workspaces = [{"name": "Designing", "type": "apps", "apps": ["figma"]}]
    analytics = AnalyticsStore(
        {
            "workspace_launches": {"Designing": 5},
            "recent_launches": [],
            "detection_history": [["Steam", "Discord"]],
        }
    )

    recommendation = recommend_workspace(workspaces, ["Unrelated App"], analytics)
    assert "No workspace matches the detected apps." in recommendation
    assert "Your most-used workspace is Designing." in recommendation
