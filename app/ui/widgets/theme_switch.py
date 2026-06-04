import customtkinter
from app.core.profiles import load_profiles, save_profiles


def load_theme() -> str:
    config = load_profiles()
    theme = config.get("settings", {}).get("theme")
    if isinstance(theme, str) and theme in ("light", "dark"):
        return theme
    return "dark"


def save_theme(theme: str) -> None:
    config = load_profiles()
    config.setdefault("settings", {})["theme"] = theme
    save_profiles(config)


class ThemeSwitch(customtkinter.CTkSwitch):
    def __init__(self, master, **kwargs):
        self.var = customtkinter.StringVar(value=load_theme())
        super().__init__(
            master,
            text="Switch Theme",
            variable=self.var,
            onvalue="light",
            offvalue="dark",
            command=self.switch_theme,
            **kwargs,
        )
        self.apply_theme()

    def switch_theme(self) -> None:
        theme = self.var.get()
        customtkinter.set_appearance_mode(theme)
        save_theme(theme)

    def apply_theme(self) -> None:
        customtkinter.set_appearance_mode(self.var.get())
