import customtkinter
from tkinter import messagebox
from pathlib import Path
from typing import Dict, Any, List
from threading import Thread

from PIL import Image
from app.core.analytics import AnalyticsStore
from app.core.detection import detect_installed_apps, get_os
from app.core.launcher import launch_workspace
from app.core.logger import logger
from app.core.profiles import load_profiles, save_profiles, get_workspaces
from app.core.recommendation import recommend_workspace
from app.plugins import notify_apps_detected
from app.ui.widgets.theme_switch import ThemeSwitch

ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets"
ICON_SIZE = (32, 32)
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def load_icon(name: str) -> customtkinter.CTkImage:
    path = ASSETS_DIR / name
    return customtkinter.CTkImage(light_image=Image.open(path), size=ICON_SIZE)


class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("App Mode Launcher")
        self.geometry("760x520")
        self.minsize(680, 480)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        self.config_data = load_profiles()
        self.workspaces = get_workspaces(self.config_data)
        self.filtered_workspaces: List[Dict[str, Any]] = self.workspaces
        self.os_name = get_os()
        self.detected_apps = detect_installed_apps()
        self.analytics = AnalyticsStore.load()
        self.analytics.track_detection(list(self.detected_apps.keys()))
        self.icons = {
            "coding": load_icon("coding_icon.png"),
            "talking": load_icon("talk_icon.png"),
            "design": load_icon("design_icon.png"),
        }

        self.spinner_index = 0
        self.workspace_buttons: List[customtkinter.CTkButton] = []

        self._setup_ui()
        self._apply_startup_behavior()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        header_frame = customtkinter.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = customtkinter.CTkLabel(
            header_frame,
            text="Choose your workspace",
            font=("JetBrains Mono ExtraBold", 32),
            anchor="w",
        )
        title_label.grid(row=0, column=0, sticky="w")

        subtitle_label = customtkinter.CTkLabel(
            header_frame,
            text="Smart workspaces, persistent themes, and automatic app detection.",
            font=("JetBrains Mono", 14),
            fg_color="transparent",
            anchor="w",
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 10))

        theme_switch = ThemeSwitch(header_frame)
        theme_switch.grid(row=0, column=1, rowspan=2, sticky="e")

        # Search/Filter frame
        filter_frame = customtkinter.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        filter_frame.grid_columnconfigure(0, weight=1)

        search_label = customtkinter.CTkLabel(
            filter_frame,
            text="Search workspaces:",
            font=("JetBrains Mono", 12),
            fg_color="transparent",
        )
        search_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.search_entry = customtkinter.CTkEntry(
            filter_frame,
            placeholder_text="Type workspace name...",
            font=("JetBrains Mono", 12),
            height=32,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._filter_workspaces())

        clear_button = customtkinter.CTkButton(
            filter_frame,
            text="Clear",
            command=self._clear_search,
            width=60,
            height=32,
            font=("JetBrains Mono", 12),
        )
        clear_button.grid(row=0, column=2, sticky="e")

        menu_frame = customtkinter.CTkFrame(self)
        menu_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        menu_frame.grid_columnconfigure(0, weight=1)

        workspace_frame = customtkinter.CTkFrame(menu_frame, corner_radius=15)
        workspace_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        workspace_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.workspace_buttons = []
        for index, workspace in enumerate(self.filtered_workspaces):
            button = customtkinter.CTkButton(
                workspace_frame,
                text=workspace.get("name", f"Modo {index + 1}"),
                command=lambda ws=workspace: self.launch_workspace(ws),
                image=self._workspace_icon(workspace),
                compound="top",
                width=180,
                height=120,
                hover_color="#4a4a4a",
            )
            button.grid(row=0, column=index, padx=8, pady=12, sticky="nsew")
            self.workspace_buttons.append(button)

        info_frame = customtkinter.CTkFrame(menu_frame, corner_radius=15)
        info_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        info_frame.grid_columnconfigure(0, weight=1)

        self.detect_button = customtkinter.CTkButton(
            info_frame,
            text="Detect installed apps",
            command=self.refresh_detection,
            width=220,
        )
        self.detect_button.grid(row=0, column=0, padx=12, pady=12, sticky="w")

        self.detected_label = customtkinter.CTkLabel(
            info_frame,
            text=self._detected_text(),
            anchor="w",
            fg_color="transparent",
            wraplength=680,
            justify="left",
        )
        self.detected_label.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        self.status_label = customtkinter.CTkLabel(
            info_frame,
            text="Ready",
            anchor="w",
            fg_color="transparent",
            text_color="#7f8c8d",
            font=("JetBrains Mono", 12),
        )
        self.status_label.grid(row=2, column=0, padx=12, pady=(0, 10), sticky="w")

        recommendation_frame = customtkinter.CTkFrame(menu_frame, corner_radius=15)
        recommendation_frame.grid(row=2, column=0, sticky="ew")
        recommendation_frame.grid_columnconfigure(0, weight=1)

        recommendation_title = customtkinter.CTkLabel(
            recommendation_frame,
            text="Auto recommendation",
            font=("JetBrains Mono ExtraBold", 16),
            anchor="w",
        )
        recommendation_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.recommendation_label = customtkinter.CTkLabel(
            recommendation_frame,
            text=self._recommendation_text(),
            fg_color="transparent",
            wraplength=700,
            justify="left",
            anchor="w",
        )
        self.recommendation_label.grid(
            row=1, column=0, sticky="w", padx=12, pady=(0, 12)
        )

        analytics_frame = customtkinter.CTkFrame(menu_frame, corner_radius=15)
        analytics_frame.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        analytics_frame.grid_columnconfigure(0, weight=1)

        analytics_title = customtkinter.CTkLabel(
            analytics_frame,
            text="Usage summary",
            font=("JetBrains Mono ExtraBold", 16),
            anchor="w",
        )
        analytics_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 4))

        self.analytics_label = customtkinter.CTkLabel(
            analytics_frame,
            text=self._analytics_text(),
            fg_color="transparent",
            wraplength=700,
            justify="left",
            anchor="w",
        )
        self.analytics_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))

        footer = customtkinter.CTkLabel(
            self,
            text=f"Operating system detected: {self.os_name}",
            font=("JetBrains Mono", 12),
            fg_color="transparent",
            anchor="w",
        )
        footer.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 16))

    def _workspace_icon(self, workspace: Dict[str, Any]) -> customtkinter.CTkImage:
        name = workspace.get("name", "").lower()
        if "code" in name or "coding" in name:
            return self.icons["coding"]
        if "talk" in name or workspace.get("type") == "talking":
            return self.icons["talking"]
        if "design" in name:
            return self.icons["design"]
        return self.icons["coding"]

    def _filter_workspaces(self) -> None:
        """Filter workspaces based on search entry and refresh display."""
        search_term = self.search_entry.get().lower().strip()

        if not search_term:
            self.filtered_workspaces = self.workspaces
        else:
            self.filtered_workspaces = [
                ws
                for ws in self.workspaces
                if search_term in ws.get("name", "").lower()
            ]

        self._rebuild_workspace_buttons()

    def _clear_search(self) -> None:
        """Clear search filter and show all workspaces."""
        self.search_entry.delete(0, "end")
        self.filtered_workspaces = self.workspaces
        self._rebuild_workspace_buttons()

    def _rebuild_workspace_buttons(self) -> None:
        """Rebuild workspace buttons based on filtered list."""
        for button in self.workspace_buttons:
            button.destroy()
        self.workspace_buttons.clear()

        # Get the workspace frame (row 0, column 0 of menu_frame)
        menu_frame_children = self.grid_slaves(row=1, column=0)
        if menu_frame_children:
            menu_frame = menu_frame_children[0]
            workspace_frame = menu_frame.grid_slaves(row=0, column=0)
            if workspace_frame:
                workspace_frame = workspace_frame[0]
                workspace_frame.grid_columnconfigure((0, 1, 2), weight=1)

                for index, workspace in enumerate(self.filtered_workspaces):
                    button = customtkinter.CTkButton(
                        workspace_frame,
                        text=workspace.get("name", f"Modo {index + 1}"),
                        command=lambda ws=workspace: self.launch_workspace(ws),
                        image=self._workspace_icon(workspace),
                        compound="top",
                        width=180,
                        height=120,
                        hover_color="#4a4a4a",
                    )
                    button.grid(row=0, column=index, padx=8, pady=12, sticky="nsew")
                    self.workspace_buttons.append(button)

    def _get_spinner_frame(self) -> str:
        """Get current spinner animation frame."""
        frame = SPINNER_FRAMES[self.spinner_index % len(SPINNER_FRAMES)]
        self.spinner_index += 1
        return frame

    def _animate_spinner(self) -> None:
        """Animate spinner while detection is running."""
        if self.detect_button.cget("state") == "disabled":
            spinner_char = self._get_spinner_frame()
            self.status_label.configure(
                text=f"{spinner_char} Detecting installed apps..."
            )
            self.after(100, self._animate_spinner)

    def _detected_text(self) -> str:
        if not self.detected_apps:
            return "No known apps detected automatically. Click detect to refresh."

        names = ", ".join(self.detected_apps.keys())
        return f"Automatically detected apps: {names}."

    def _recommendation_text(self) -> str:
        return recommend_workspace(
            self.workspaces, list(self.detected_apps.keys()), self.analytics
        )

    def _set_status_message(self, message: str, level: str = "info") -> None:
        color_map = {
            "info": "#7f8c8d",
            "success": "#2ecc71",
            "warning": "#f1c40f",
            "error": "#e74c3c",
        }
        self.status_label.configure(
            text=message, text_color=color_map.get(level, "#7f8c8d")
        )

    def _apply_startup_behavior(self) -> None:
        startup = self.config_data.get("settings", {}).get("startup", {})
        if not startup.get("auto_launch"):
            return

        workspace_name = startup.get("workspace_name", "")
        if startup.get("resume_last_workspace"):
            workspace_name = workspace_name or startup.get("last_workspace", "")

        if not workspace_name:
            return

        preferred = next(
            (
                workspace
                for workspace in self.workspaces
                if workspace.get("name") == workspace_name
            ),
            None,
        )

        if preferred:
            logger.info("Auto-launching workspace: %s", workspace_name)
            self.launch_workspace(preferred)

    def _analytics_text(self) -> str:
        total_launches = self.analytics.get_total_launches()
        total_detections = self.analytics.get_total_detections()
        top_workspace = self.analytics.get_top_workspace()
        last_workspace = self.analytics.get_last_workspace()

        lines = [
            f"Total workspace launches: {total_launches}",
            f"Total app detections: {total_detections}",
        ]

        if top_workspace:
            lines.append(f"Most-used workspace: {top_workspace}")
        if last_workspace:
            lines.append(f"Last launched workspace: {last_workspace}")

        return "\n".join(lines)

    def refresh_detection(self) -> None:
        """Detect installed apps with visual feedback and spinner animation."""
        logger.debug("refresh_detection called")
        self.detect_button.configure(state="disabled")
        self.spinner_index = 0
        self._animate_spinner()

        def _detect_in_background() -> None:
            try:
                self.detected_apps = detect_installed_apps()
                self.analytics.track_detection(list(self.detected_apps.keys()))
                notify_apps_detected(list(self.detected_apps.keys()))

                self.after(
                    0, lambda: self.detected_label.configure(text=self._detected_text())
                )
                self.after(
                    0,
                    lambda: self.recommendation_label.configure(
                        text=self._recommendation_text()
                    ),
                )
                self.after(
                    0,
                    lambda: self.analytics_label.configure(text=self._analytics_text()),
                )
                self.after(
                    0,
                    lambda: self._set_status_message(
                        "✓ Detection completed successfully.", "success"
                    ),
                )
                logger.info("App detection refreshed successfully")
            except Exception as exc:
                self.after(
                    0,
                    lambda: self._set_status_message(
                        "✗ Detection failed. Check logs for details.", "error"
                    ),
                )
                logger.exception("Error during app detection: %s", exc)
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Detection Error", "An error occurred while detecting apps."
                    ),
                )
            finally:
                self.after(0, lambda: self.detect_button.configure(state="normal"))

        detection_thread = Thread(target=_detect_in_background, daemon=True)
        detection_thread.start()

    def launch_workspace(self, workspace: Dict[str, Any]) -> None:
        """Launch workspace with contextual feedback."""
        logger.debug("launch_workspace UI called for workspace=%s", workspace)
        ws_name = workspace.get("name", "unknown")
        ws_type = workspace.get("type", "apps")

        if ws_type == "talking" and not workspace.get("aumid"):
            logger.warning("Workspace launch failed: missing AUMID")
            self._set_status_message(
                f'✗ Launch failed: AUMID missing for "{ws_name}" (talking).', "error"
            )
            messagebox.showerror(
                "Error", "AUMID is not configured for the talking workspace."
            )
            return

        try:
            self._set_status_message(f'◐ Launching "{ws_name}"...', "info")
            launch_workspace(workspace)
            self.config_data.setdefault("settings", {}).setdefault("startup", {})[
                "last_workspace"
            ] = ws_name
            save_profiles(self.config_data)

            feedback = {
                "talking": f'✓ "{ws_name}" (talking mode) launched successfully.',
                "apps": f'✓ "{ws_name}" launched with {len(workspace.get("apps", []))} app(s).',
            }
            message = feedback.get(ws_type, f'✓ "{ws_name}" launched successfully.')
            self._set_status_message(message, "success")
            logger.info("Workspace launched: %s (type: %s)", ws_name, ws_type)
        except Exception as exc:
            self._set_status_message(
                f'✗ Launch failed for "{ws_name}". Check logs for details.', "error"
            )
            logger.exception("Workspace launch error: %s", exc)
            messagebox.showerror(
                "Launch Error", f'Failed to launch "{ws_name}". Check logs for details.'
            )
            return
        self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
