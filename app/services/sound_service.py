"""Lightweight typing feedback sound using wrong-character sounds - PySide6 QSoundEffect."""
from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

from ..core.config import resource_path


class SoundService:
    """Plays a wrong-character sound when an incorrect keystroke is typed.

    Only one sound category is active: Wrong Character Sound.
    Users can select from 6 distinct sound options and adjust volume.
    Selection and volume are persisted in application settings.
    """

    DEFAULT_VOLUME = 0.75  # 75% default volume

    # Six distinct wrong-character sound options
    SOUND_NAMES = [
        "wrong_soft_beep",
        "wrong_classic_error",
        "wrong_digital_error",
        "wrong_mechanical_click",
        "wrong_low_tone",
        "wrong_alert_tone",
    ]

    def __init__(self, parent=None):
        self._parent = parent
        self._enabled = True
        self._sound_index = 0  # which wrong-character sound to play (0-5)
        self._volume = self.DEFAULT_VOLUME

        # Load sound file paths for all 6 wrong-character options
        sounds_dir = resource_path("sounds")
        self._error_sound_paths = [
            sounds_dir / f"{name}.wav" for name in self.SOUND_NAMES
        ]

        # Create a single QSoundEffect for playback
        self._error_effect = QSoundEffect(self._parent)

        # Configure the effect
        self._error_effect.setLoopCount(1)
        self._error_effect.setVolume(self._volume)

        # Pre-load all sources so they are ready
        for path in self._error_sound_paths:
            if path.exists():
                self._error_effect.setSource(QUrl.fromLocalFile(str(path)))

    def set_enabled(self, enabled: bool):
        """Enable/disable wrong-character sound."""
        self._enabled = bool(enabled)

    def set_sound(self, index: int):
        """Select which wrong-character sound to play (0-5). Clamp to valid range."""
        self._sound_index = max(0, min(len(self.SOUND_NAMES) - 1, int(index)))
        path = self._error_sound_paths[self._sound_index]
        if path.exists():
            self._error_effect.setSource(QUrl.fromLocalFile(str(path)))
            # Ensure volume is applied
            self._error_effect.setVolume(self._volume)

    def get_sound_index(self) -> int:
        """Return the currently selected sound index (0-5)."""
        return self._sound_index

    def set_volume(self, volume: float):
        """Set volume (0.0 to 1.0). Applied to the effect immediately."""
        self._volume = max(0.0, min(1.0, float(volume)))
        if self._enabled:
            self._error_effect.setVolume(self._volume)

    def get_volume(self) -> float:
        """Get current volume level (0.0 to 1.0)."""
        return self._volume

    def is_enabled(self) -> bool:
        return self._enabled

    def play_error(self):
        """Play the selected wrong-character sound.

        Must be called on incorrect keystroke. Only plays if enabled
        and the selected sound source is ready.
        Ensures no unnecessary delay between typing and sound.
        """
        if not self._enabled:
            return
        # Ensure source is set for the selected sound
        path = self._error_sound_paths[self._sound_index]
        if path.exists():
            self._error_effect.setSource(QUrl.fromLocalFile(str(path)))
        # Set volume before play
        self._error_effect.setVolume(self._volume)
        # Only play if ready or null (avoid overlapping/noise issues)
        if self._error_effect.status() in (QSoundEffect.Ready, QSoundEffect.Null):
            self._error_effect.play()