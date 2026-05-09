from typing import Dict

from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication


def is_dark_mode() -> bool:
    app = QApplication.instance()
    if app is None:
        return True

    window_color = app.palette().color(QPalette.Window)
    return window_color.lightness() < 128


def colors() -> Dict[str, str]:
    if is_dark_mode():
        return {
            "window": "#141416",
            "panel": "#1c1c1e",
            "panel_border": "#3a3a3c",
            "tile": "#2c2c2e",
            "tile_border": "#3a3a3c",
            "text": "#f2f2f7",
            "muted_text": "#8e8e93",
            "selected_bg": "#0a84ff33",
            "selected_border": "#0a84ff",
            "selected_text": "#f2f2f7",
            "progress_track": "#3a3a3c",
            "button_primary": "#2f3644",
            "button_primary_border": "#495266",
            "button_primary_hover": "#394155",
            "button_primary_hover_border": "#5b6680",
            "button_secondary": "#2d3338",
            "button_secondary_border": "#445057",
            "button_secondary_hover": "#373f45",
            "button_secondary_hover_border": "#56636b",
            "button_neutral": "#262628",
            "button_neutral_border": "#37373b",
            "button_neutral_hover": "#2f2f33",
            "button_neutral_hover_border": "#47474d",
            "button_pressed": "#242427",
            "button_text": "#f2f2f7",
            "correct": "#30d158",
            "partial": "#ffd60a",
            "wrong": "#ff453a",
            "result_text": "#ffffff",
        }

    return {
        "window": "#f7f8fa",
        "panel": "#ffffff",
        "panel_border": "#d8dde5",
        "tile": "#eef1f5",
        "tile_border": "#d4dae3",
        "text": "#20242a",
        "muted_text": "#69717d",
        "selected_bg": "#d9e9ff",
        "selected_border": "#4b8fd8",
        "selected_text": "#1f3650",
        "progress_track": "#e4e8ee",
        "button_primary": "#edf1f7",
        "button_primary_border": "#cfd7e3",
        "button_primary_hover": "#e2e8f1",
        "button_primary_hover_border": "#bdc8d7",
        "button_secondary": "#f1f4f8",
        "button_secondary_border": "#d5dce6",
        "button_secondary_hover": "#e6ebf2",
        "button_secondary_hover_border": "#c4ceda",
        "button_neutral": "#ffffff",
        "button_neutral_border": "#d8dde5",
        "button_neutral_hover": "#f0f3f7",
        "button_neutral_hover_border": "#c8d0db",
        "button_pressed": "#dde3eb",
        "button_text": "#20242a",
        "correct": "#34c759",
        "partial": "#f0b429",
        "wrong": "#ff453a",
        "result_text": "#ffffff",
    }


def panel_style() -> str:
    c = colors()
    return f"""
        QFrame {{
            background: {c["panel"]};
            border: 1px solid {c["panel_border"]};
            border-radius: 24px;
        }}
    """


def transparent_label_style(color_key: str = "text") -> str:
    c = colors()
    return (
        f"color: {c[color_key]}; background: transparent; border: none; "
        "padding: 0px; margin: 0px;"
    )
