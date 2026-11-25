from __future__ import annotations

from dataclasses import dataclass

from ..core.config import user_data_dir
from ..core.layouts import Layout, load_layouts
from ..database.connection import Database
from ..database.repositories import SettingsRepo, UserRepo
from ..services.sound_service import SoundService
from .content_service import ContentService
from .progress_service import ProgressService
from .settings_service import SettingsService


@dataclass
class AppContext:
    db: Database
    settings: SettingsService
    content: ContentService
    progress: ProgressService
    layouts: dict[str, Layout]
    sound_service: SoundService | None = None


def build_context(db_path=None) -> AppContext:
    db = Database(db_path or user_data_dir() / "persiantype.db")
    UserRepo(db).ensure_default()
    settings = SettingsService(SettingsRepo(db))
    content = ContentService(settings)
    progress = ProgressService(db)
    for variant in ("iranian_persian", "dari"):
        progress.lessons.sync(content.lessons(variant))
    return AppContext(db, settings, content, progress, load_layouts(), SoundService())
