"""Tests for the wrong-character sound system."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtCore import QCoreApplication
from PySide6.QtMultimedia import QSoundEffect

from app.services.sound_service import SoundService


def test_default_sound_disabled():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    # By default enabled
    assert svc.is_enabled()


def test_sound_selection():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    # Select each sound
    for i in range(len(SoundService.SOUND_NAMES)):
        svc.set_sound(i)
        assert svc.get_sound_index() == i
    # Clamp invalid index
    svc.set_sound(99)
    assert svc.get_sound_index() == len(SoundService.SOUND_NAMES) - 1
    svc.set_sound(-1)
    assert svc.get_sound_index() == 0


def test_volume_clamp():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    svc.set_volume(1.5)
    assert svc.get_volume() == 1.0
    svc.set_volume(-0.5)
    assert svc.get_volume() == 0.0


def test_sound_files_exist():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    for path in svc._error_sound_paths:
        assert path.exists(), f"Missing sound file: {path}"


def test_play_error_when_enabled():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    svc.set_enabled(True)
    svc.set_volume(0.1)
    svc.play_error()


def test_play_error_when_disabled():
    app = QCoreApplication.instance() or QCoreApplication(sys.argv)
    svc = SoundService()
    svc.set_enabled(False)
    svc.set_volume(0.1)
    svc.play_error()  # Should not crash

