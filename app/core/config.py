from __future__ import annotations

import os
import sys
from pathlib import Path

from .constants import APP_NAME


def base_dir() -> Path:
    if getattr(sys, "frozen", False):  # PyInstaller
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[2]


def resource_path(*parts: str) -> Path:
    return base_dir().joinpath("app", "resources", *parts)


def content_path(*parts: str) -> Path:
    return base_dir().joinpath("content", *parts)


def user_data_dir() -> Path:
    root = os.environ.get("APPDATA") or str(Path.home() / ".local" / "share")
    path = Path(root) / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path
