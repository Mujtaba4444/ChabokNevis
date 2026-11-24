"""Lightweight typing sound feedback using local WAV resources - mechanical keyboard style."""
from __future__ import annotations

import random
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QSoundEffect

from ..core.config import resource_path


class SoundService:
    """Plays mechanical keyboard style sounds for typing feedback."""

    DEFAULT_VOLUME = 0.75  # 75% default volume

    def __init__(self, parent=None):
        self._parent = parent
        self._enabled = True
        self._sound_correct_enabled = True
        self._sound_error_enabled = True
        self._volume = self.DEFAULT_VOLUME

        # Load sound file paths
        sounds_dir = resource_path("sounds")
        self._click_sounds = [
            sounds_dir / f"click_{i}.wav" for i in range(5)
        ]
        self._error_sounds = [
            sounds_dir / f"error_{i}.wav" for i in range(3)
        ]
        self._space_sound = sounds_dir / "space.wav"

        # Create QSoundEffect instances for each sound (allows overlapping playback)
        self._click_effects = [QSoundEffect(self._parent) for _ in self._click_sounds]
        self._error_effects = [QSoundEffect(self._parent) for _ in self._error_sounds]
        self._space_effect = QSoundEffect(self._parent)

        # Configure all effects
        all_effects = self._click_effects + self._error_effects + [self._space_effect]
        for effect in all_effects:
            effect.setLoopCount(1)
            effect.setVolume(self._volume)

        # Pre-load sources
        for effect, path in zip(self._click_effects, self._click_sounds):
            if path.exists():
                effect.setSource(QUrl.fromLocalFile(str(path)))
        for effect, path in zip(self._error_effects, self._error_sounds):
            if path.exists():
                effect.setSource(QUrl.fromLocalFile(str(path)))
        if self._space_sound.exists():
            self._space_effect.setSource(QUrl.fromLocalFile(str(self._space_sound)))

        self._click_index = 0
        self._error_index = 0

    def set_enabled(self, enabled: bool):
        """Master enable/disable for all typing sounds."""
        self._enabled = bool(enabled)

    def set_sound_correct(self, enabled: bool):
        """Enable/disable correct keypress sounds."""
        self._sound_correct_enabled = bool(enabled)

    def set_sound_error(self, enabled: bool):
        """Enable/disable error sounds."""
        self._sound_error_enabled = bool(enabled)

    def set_volume(self, volume: float):
        """Set volume for all typing sounds (0.0 to 1.0)."""
        self._volume = max(0.0, min(1.0, float(volume)))
        all_effects = self._click_effects + self._error_effects + [self._space_effect]
        for effect in all_effects:
            effect.setVolume(self._volume)

    def get_volume(self) -> float:
        """Get current volume level (0.0 to 1.0)."""
        return self._volume

    def is_enabled(self) -> bool:
        return self._enabled

    def play_click(self):
        """Play a mechanical key click sound (round-robin for variation)."""
        if not self._enabled or not self._sound_correct_enabled:
            return
        effect = self._click_effects[self._click_index]
        if effect.status() == QSoundEffect.Ready or effect.status() == QSoundEffect.Stopped:
            effect.play()
        self._click_index = (self._click_index + 1) % len(self._click_effects)

    def play_space(self):
        """Play spacebar thock sound."""
        if not self._enabled or not self._sound_correct_enabled:
            return
        if self._space_effect.status() == QSoundEffect.Ready or self._space_effect.status() == QSoundEffect.Stopped:
            self._space_effect.play()

    def play_error(self):
        """Play error sound (distinct from normal clicks)."""
        if not self._enabled or not self._sound_error_enabled:
            return
        effect = self._error_effects[self._error_index]
        if effect.status() == QSoundEffect.Ready or effect.status() == QSoundEffect.Stopped:
            effect.play()
        self._error_index = (self._error_index + 1) % len(self._error_effects)