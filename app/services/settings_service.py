from PySide6.QtCore import QObject, Signal

from ..core.constants import DEFAULT_SETTINGS


class SettingsService(QObject):
    changed = Signal(str)

    def __init__(self, repo):
        super().__init__()
        self.repo = repo
        self._v = {**DEFAULT_SETTINGS, **repo.load()}

    def get(self, key):
        return self._v.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        if self._v.get(key) == value:
            return
        self._v[key] = value
        self.repo.save(key, value)
        self.changed.emit(key)
