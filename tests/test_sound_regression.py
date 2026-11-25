"""Regression tests for sound system settings handling."""
import sys
from pathlib import Path
import tempfile
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication
from app.database.connection import Database
from app.database.repositories import SettingsRepo, UserRepo
from app.services.settings_service import SettingsService
from app.services.sound_service import SoundService
from app.ui.widgets.typing_panel import TypingPanel
from app.services.context import build_context


def test_fresh_install_no_settings():
    """Test fresh application installation with no existing settings."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        UserRepo(db).ensure_default()

        repo = SettingsRepo(db)
        settings = SettingsService(repo)

        # Should get default values
        assert settings.get("sound_index") == 0
        assert settings.get("sound_volume") == 75
        assert settings.get("sound") == False

        # Create sound service and verify it works
        svc = SoundService()
        svc.set_sound(settings.get("sound_index"))
        svc.set_volume(settings.get("sound_volume") / 100.0)
        svc.play_error()  # Should not crash

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_legacy_settings_no_sound_index():
    """Test existing user settings from previous version (no sound_index)."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        UserRepo(db).ensure_default()

        repo = SettingsRepo(db)
        # Legacy settings: sound and volume but no sound_index
        repo.save("sound", True)
        repo.save("sound_volume", 50)

        settings = SettingsService(repo)

        # Should fall back to default sound_index
        assert settings.get("sound_index") == 0
        assert settings.get("sound_volume") == 50
        assert settings.get("sound") == True

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_explicit_null_sound_index():
    """Test handling of explicit null sound_index in database."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        UserRepo(db).ensure_default()

        repo = SettingsRepo(db)
        repo.save("sound", True)
        repo.save("sound_volume", 50)
        repo.save("sound_index", None)  # Explicitly null

        settings = SettingsService(repo)

        # Should handle None and return default
        assert settings.get("sound_index") == 0
        assert isinstance(settings.get("sound_index"), int)

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_invalid_sound_index():
    """Test handling of invalid sound index values."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        UserRepo(db).ensure_default()

        repo = SettingsRepo(db)
        repo.save("sound_index", "invalid")  # String instead of int
        repo.save("sound_volume", 50)

        settings = SettingsService(repo)

        # SoundService should handle invalid values gracefully
        svc = SoundService()
        svc.set_sound(settings.get("sound_index"))  # Should not crash
        assert svc.get_sound_index() == 0  # Clamped to valid range

        # Test out of range
        repo.save("sound_index", 99)
        settings = SettingsService(repo)
        svc.set_sound(settings.get("sound_index"))
        assert svc.get_sound_index() == 5  # Clamped to max (5)

        # Test negative
        repo.save("sound_index", -1)
        settings = SettingsService(repo)
        svc.set_sound(settings.get("sound_index"))
        assert svc.get_sound_index() == 0  # Clamped to min (0)

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_changing_selected_sound():
    """Test changing the selected sound updates sound service immediately."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        db = Database(db_path)
        UserRepo(db).ensure_default()

        repo = SettingsRepo(db)
        settings = SettingsService(repo)
        svc = SoundService()

        # Change sound index
        for idx in range(6):
            settings.set("sound_index", idx)
            svc.set_sound(settings.get("sound_index"))
            assert svc.get_sound_index() == idx

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_preview_button_repeated_clicks():
    """Test clicking Preview repeatedly doesn't cause conflicts."""
    app = QApplication.instance() or QApplication(sys.argv)

    svc = SoundService()
    svc.set_sound(0)
    svc.set_volume(0.5)

    # Multiple rapid clicks should not crash
    for _ in range(10):
        svc.play_error()

    app.quit()


def test_typing_incorrect_characters():
    """Test typing incorrect characters plays sound."""
    app = QApplication.instance() or QApplication(sys.argv)

    ctx = build_context()
    panel = TypingPanel(ctx)

    panel.start("hello")
    panel.ctx.settings.set("accept_latin", False)
    panel.ctx.settings.set("sound", True)
    panel.ctx.settings.set("sound_index", 0)
    panel.ctx.settings.set("sound_volume", 50)
    panel.apply_settings()

    # Type incorrect character
    panel._on_char("x")  # Should play error sound
    panel._on_char("y")  # Should play error sound

    # Type correct characters (should not play sound)
    panel._on_char("h")
    panel._on_char("e")

    app.quit()


def test_settings_persistence_across_restart():
    """Test settings persist after application restart."""
    app = QApplication.instance() or QApplication(sys.argv)

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        # First "session" - save settings
        db1 = Database(db_path)
        UserRepo(db1).ensure_default()

        repo1 = SettingsRepo(db1)
        settings1 = SettingsService(repo1)
        settings1.set("sound_index", 3)
        settings1.set("sound_volume", 80)
        settings1.set("sound", True)

        # Simulate restart - new connection to same DB
        db2 = Database(db_path)
        UserRepo(db2).ensure_default()

        repo2 = SettingsRepo(db2)
        settings2 = SettingsService(repo2)

        # Settings should persist
        assert settings2.get("sound_index") == 3
        assert settings2.get("sound_volume") == 80
        assert settings2.get("sound") == True

    finally:
        try:
            os.unlink(db_path)
        except:
            pass

    app.quit()


def test_language_switching():
    """Test switching between English and Persian/Dari."""
    app = QApplication.instance() or QApplication(sys.argv)

    ctx = build_context()

    # Test English
    ctx.settings.set("ui_language", "en")
    ctx.settings.set("sound_index", 2)
    ctx.settings.set("sound_volume", 60)

    svc = SoundService()
    svc.set_sound(ctx.settings.get("sound_index"))
    svc.set_volume(ctx.settings.get("sound_volume") / 100.0)
    assert svc.get_sound_index() == 2
    assert svc.get_volume() == 0.6

    # Switch to Dari
    ctx.settings.set("ui_language", "fa_AF")
    # Settings should persist
    assert ctx.settings.get("sound_index") == 2
    assert ctx.settings.get("sound_volume") == 60

    app.quit()


def test_sound_service_set_sound_robustness():
    """Test SoundService.set_sound handles various edge cases."""
    app = QApplication.instance() or QApplication(sys.argv)

    svc = SoundService()

    # None
    svc.set_sound(None)
    assert svc.get_sound_index() == 0

    # String number
    svc.set_sound("3")
    assert svc.get_sound_index() == 3

    # Float
    svc.set_sound(4.7)
    assert svc.get_sound_index() == 4

    # Out of range high
    svc.set_sound(100)
    assert svc.get_sound_index() == 5

    # Out of range low
    svc.set_sound(-10)
    assert svc.get_sound_index() == 0

    # Invalid string
    svc.set_sound("abc")
    assert svc.get_sound_index() == 0

    app.quit()


if __name__ == '__main__':
    test_fresh_install_no_settings()
    print("✓ test_fresh_install_no_settings")

    test_legacy_settings_no_sound_index()
    print("✓ test_legacy_settings_no_sound_index")

    test_explicit_null_sound_index()
    print("✓ test_explicit_null_sound_index")

    test_invalid_sound_index()
    print("✓ test_invalid_sound_index")

    test_changing_selected_sound()
    print("✓ test_changing_selected_sound")

    test_preview_button_repeated_clicks()
    print("✓ test_preview_button_repeated_clicks")

    test_typing_incorrect_characters()
    print("✓ test_typing_incorrect_characters")

    test_settings_persistence_across_restart()
    print("✓ test_settings_persistence_across_restart")

    test_language_switching()
    print("✓ test_language_switching")

    test_sound_service_set_sound_robustness()
    print("✓ test_sound_service_set_sound_robustness")

    print("\nAll regression tests passed!")