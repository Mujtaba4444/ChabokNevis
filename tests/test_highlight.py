"""Tests for character highlighting in typing panel."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PySide6.QtWidgets import QApplication
from app.ui.widgets.typing_panel import TypingPanel
from app.services.context import build_context


def test_highlighting_all_correct():
    """Test that all correct characters are highlighted green."""
    app = QApplication.instance() or QApplication(sys.argv)
    ctx = build_context()
    panel = TypingPanel(ctx)

    # Test with English text (LTR)
    panel.start('hello')
    panel.ctx.settings.set('accept_latin', False)

    # Type all correct characters
    for ch in 'hello':
        panel._on_char(ch)

    selections = panel.area.extraSelections()
    assert len(selections) == 5, f"Expected 5 selections, got {len(selections)}"

    # All should be green (success) with white background
    for sel in selections:
        fmt = sel.format
        fg = fmt.foreground().color()
        bg = fmt.background().color()
        assert fg.name() == '#16a34a', f"Expected green foreground, got {fg.name()}"
        assert bg.name() == '#ffffff', f"Expected white background, got {bg.name()}"

    app.quit()


def test_highlighting_mixed_correct_incorrect():
    """Test mixed correct and incorrect characters."""
    app = QApplication.instance() or QApplication(sys.argv)
    ctx = build_context()
    panel = TypingPanel(ctx)

    panel.start('hello')
    panel.ctx.settings.set('accept_latin', False)

    # Type: h (correct), x (incorrect), e (correct), l (correct), l (correct), o (correct)
    panel._on_char('h')
    panel._on_char('x')
    panel._on_char('e')
    panel._on_char('l')
    panel._on_char('l')
    panel._on_char('o')

    selections = panel.area.extraSelections()
    # Should have 5 selections (one per character in "hello")
    assert len(selections) == 5, f"Expected 5 selections, got {len(selections)}"

    # Check: h=green, x=red, e=red (wrong position), l=green, l=red (wrong position)
    expected_colors = [
        '#16a34a',  # h - correct
        '#dc2626',  # x - incorrect
        '#dc2626',  # e - incorrect (position 2 expected 'l')
        '#16a34a',  # l - correct (position 3)
        '#dc2626',  # l - incorrect (position 4 expected 'o')
    ]

    for i, sel in enumerate(selections):
        fmt = sel.format
        fg = fmt.foreground().color()
        assert fg.name() == expected_colors[i], f"Selection {i}: expected {expected_colors[i]}, got {fg.name()}"

    app.quit()


def test_highlighting_persian_correct():
    """Test Persian text highlighting with correct keys."""
    app = QApplication.instance() or QApplication(sys.argv)
    ctx = build_context()
    panel = TypingPanel(ctx)

    # "سلام" requires keys: s, g, h, l in Persian Windows layout
    panel.start('سلام')
    panel.ctx.settings.set('accept_latin', True)

    for ch in ['s', 'g', 'h', 'l']:
        panel._on_char(ch)

    selections = panel.area.extraSelections()
    assert len(selections) == 4, f"Expected 4 selections, got {len(selections)}"

    # All should be green with white background
    for sel in selections:
        fmt = sel.format
        fg = fmt.foreground().color()
        bg = fmt.background().color()
        assert fg.name() == '#16a34a', f"Expected green foreground, got {fg.name()}"
        assert bg.name() == '#ffffff', f"Expected white background, got {bg.name()}"

    app.quit()


def test_highlighting_incorrect_char_has_red_background():
    """Test that incorrect characters have red background."""
    app = QApplication.instance() or QApplication(sys.argv)
    ctx = build_context()
    panel = TypingPanel(ctx)

    panel.start('hello')
    panel.ctx.settings.set('accept_latin', False)

    # Type incorrect character
    panel._on_char('x')

    selections = panel.area.extraSelections()
    assert len(selections) >= 1

    # First selection should be red with red background
    fmt = selections[0].format
    fg = fmt.foreground().color()
    bg = fmt.background().color()
    assert fg.name() == '#dc2626', f"Expected red foreground, got {fg.name()}"
    assert bg.name() == '#fee2e2', f"Expected red background, got {bg.name()}"

    app.quit()


if __name__ == '__main__':
    test_highlighting_all_correct()
    test_highlighting_mixed_correct_incorrect()
    test_highlighting_persian_correct()
    test_highlighting_incorrect_char_has_red_background()
    print("All highlighting tests passed!")