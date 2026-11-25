"""Typing area + live stats + virtual keyboard, shared by Learn / Practice / Speed Test."""
from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextOption, QColor
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QPlainTextEdit, QTextEdit, QVBoxLayout, QWidget

from ...i18n import tr, translator
from ...engine.statistics_engine import accuracy, wpm
from ...engine.text_normalizer import RELAXED, STRICT, ZWNJ
from ...engine.typing_engine import TypingEngine
from ...services.sound_service import SoundService
from .. import theme
from .common import Card
from .virtual_keyboard import SPACE, VirtualKeyboard


class TypingArea(QPlainTextEdit):
    charTyped = Signal(str)
    backspacePressed = Signal()
    escapePressed = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("typingArea")
        self.setReadOnly(True)
        self.setCursorWidth(0)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumHeight(170)
        opt = self.document().defaultTextOption()
        opt.setTextDirection(Qt.RightToLeft)
        opt.setAlignment(Qt.AlignRight | Qt.AlignAbsolute)
        opt.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.document().setDefaultTextOption(opt)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Backspace:
            self.backspacePressed.emit()
        elif e.key() == Qt.Key_Escape:
            self.escapePressed.emit()
        elif not (e.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier)):
            t = e.text()
            if len(t) == 1 and (t == ZWNJ or t.isprintable()):
                self.charTyped.emit(t)

    def inputMethodEvent(self, e):
        for ch in e.commitString():
            self.charTyped.emit(ch)

    def focusNextPrevChild(self, _next):
        return False

    def mousePressEvent(self, e):
        self.setFocus()

    def mouseMoveEvent(self, e):
        pass

    def mouseDoubleClickEvent(self, e):
        self.setFocus()


class TypingPanel(QWidget):
    finished = Signal(dict)

    def __init__(self, ctx, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.engine: TypingEngine | None = None
        self.duration = None
        self.extender = None
        self.rules = RELAXED
        self._t0 = None
        self._active = False
        self._sel: list = []
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._tick)

        stats = QHBoxLayout()
        self.time_v, self.wpm_v, self.acc_v = QLabel("00:00"), QLabel("0"), QLabel("100%")
        for title_key, v in (("typing.time", self.time_v), ("typing.wpm", self.wpm_v), ("typing.accuracy", self.acc_v)):
            card = Card()
            t = QLabel(); t.setObjectName("muted")
            translator.bind(t, title_key)
            v.setObjectName("cardValue")
            card.box.addWidget(t); card.box.addWidget(v)
            stats.addWidget(card)

        self.area = TypingArea()
        self.area.charTyped.connect(self._on_char)
        self.area.backspacePressed.connect(self._on_backspace)
        translator.bind(self.area, "typing.area_tip", "setToolTip")
        translator.languageChanged.connect(lambda _c: (self._update_hint(), self._update_stats()) if self.engine else None)
        self.hint = QLabel("")
        self.hint.setObjectName("muted")
        self.keyboard = VirtualKeyboard()
        # Use shared sound service from application context (one service for all typing panels)
        self.sound_service = ctx.sound_service

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(stats)
        root.addWidget(self.area, 1)
        root.addWidget(self.hint)
        root.addWidget(self.keyboard)
        ctx.settings.changed.connect(lambda _k: self.apply_settings())
        self.apply_settings()
        # Ensure minimum height is responsive to window size
        self.setMinimumHeight(0)

    # ---- settings -------------------------------------------------------
    def apply_settings(self):
        s = self.ctx.settings
        f = QFont()
        f.setFamilies([s.get("font_family"), "Vazirmatn", "Tahoma", "Segoe UI"])
        f.setPointSize(int(s.get("font_size")))
        self.area.setFont(f)
        self.layout_obj = self.ctx.layouts.get(s.get("keyboard_layout")) or next(iter(self.ctx.layouts.values()))
        self.keyboard.set_layout(self.layout_obj)
        self.keyboard.setVisible(bool(s.get("show_keyboard")))
        self.sound_service.set_enabled(bool(s.get("sound")))
        self.sound_service.set_sound(int(s.get("sound_index")))
        self.sound_service.set_volume(s.get("sound_volume") / 100.0)
        self._rebuild()

    # ---- session control -------------------------------------------------
    @property
    def is_running(self) -> bool:
        return self._active

    def start(self, text: str, duration: float | None = None, extender=None):
        self.timer.stop()
        self.rules = STRICT if self.ctx.settings.get("strict_mode") else RELAXED
        self.engine = TypingEngine(text, self.rules)
        self.duration, self.extender = duration, extender
        self._t0, self._active = None, True
        self.area.setPlainText(self.engine.target)
        self._sel = []
        self._update_stats()
        self._render()
        self.area.setFocus()

    def stop(self):
        self._active = False
        self.timer.stop()

    def finish(self):
        """End the session; emits `finished` if anything was typed."""
        if not self._active or not self.engine:
            return
        self.stop()
        if self.engine.keystrokes == 0:
            return
        secs = self._elapsed()
        if self.duration:
            secs = min(secs, self.duration)
        res = self.engine.result(secs)
        res["completed_text"] = self.engine.finished
        self.finished.emit(res)

    # ---- input -----------------------------------------------------------
    def _on_char(self, ch: str):
        if not self._active or not self.engine:
            return
        if self.ctx.settings.get("accept_latin"):
            ch = self.layout_obj.map_input(ch)
        if self._t0 is None:
            self._t0 = time.monotonic()
            self.timer.start()
        ok = self.engine.type_char(ch)
        if ok is None:
            return
        self._sel.append(self._make_sel(self.engine.position - 1, ok))
        loc = self.layout_obj.locate(ch)
        self.keyboard.flash(SPACE if ch == " " else (loc[0] if loc else None), ok)
        if self.ctx.settings.get("sound"):
            if not ok:
                # Only wrong-character sound; correct keystrokes produce no sound
                self.sound_service.play_error()
        if self.extender and len(self.engine.target) - self.engine.position < 40:
            more = " " + self.extender()
            self.engine.extend(more)
            c = QTextCursor(self.area.document())
            c.movePosition(QTextCursor.End)
            c.insertText(more)
        self._render()
        if self.engine.finished:
            self.finish()

    def _on_backspace(self):
        if self._active and self.engine and self.engine.backspace():
            self._sel.pop()
            self._render()

    # ---- rendering ---------------------------------------------------------
    def _make_sel(self, i: int, ok: bool | None):
        c = theme.colors()
        fmt = QTextCharFormat()
        if ok is True:
            fmt.setForeground(QColor(c["success"]))
            fmt.setBackground(QColor(c["card"]))  # Explicit background for correct chars
        elif ok is False:
            fmt.setForeground(QColor(c["error"]))
            fmt.setBackground(QColor(c["error_bg"]))
        else:  # current character
            fmt.setBackground(QColor(c["cur_bg"]))
        cur = QTextCursor(self.area.document())
        cur.setPosition(i)
        cur.setPosition(i + 1, QTextCursor.KeepAnchor)
        sel = QTextEdit.ExtraSelection()
        sel.cursor, sel.format = cur, fmt
        return sel

    def _rebuild(self):
        if not self.engine:
            return
        self._sel = [self._make_sel(i, s.name == "CORRECT") for i, s in enumerate(self.engine.states()[:self.engine.position])]
        self._render()

    def _render(self):
        if not self.engine:
            return
        sels = list(self._sel)
        if not self.engine.finished:
            sels.append(self._make_sel(self.engine.position, None))
        self.area.setExtraSelections(sels)
        tc = QTextCursor(self.area.document())
        tc.setPosition(min(self.engine.position, len(self.engine.target)))
        self.area.setTextCursor(tc)
        self.area.ensureCursorVisible()
        self._update_hint()

    def _update_hint(self):
        ch = self.engine.expected
        if ch is None:
            self.hint.setText("")
            self.keyboard.set_target(None)
            return
        if ch == " ":
            self.hint.setText(tr("typing.next_space"))
            self.keyboard.set_target(SPACE)
            return
        loc = self.layout_obj.locate(ch)
        if loc:
            key, shift = loc
            self.hint.setText(tr("typing.next", ch=ch, finger=tr(f"finger.{key.finger}")) + (tr("typing.shift") if shift else ""))
            self.keyboard.set_target(key, shift)
        else:
            self.hint.setText(tr("typing.next", ch=ch, finger=""))
            self.keyboard.set_target(None)

    def _elapsed(self) -> float:
        return 0.0 if self._t0 is None else time.monotonic() - self._t0

    def _tick(self):
        if self.duration and self._elapsed() >= self.duration:
            self.finish()
        else:
            self._update_stats()

    def _update_stats(self):
        secs = self._elapsed()
        shown = max(0, self.duration - secs) if self.duration else secs
        self.time_v.setText(translator.localize(f"{int(shown) // 60:02d}:{int(shown) % 60:02d}"))
        if self.engine and secs >= 1:
            self.wpm_v.setText(translator.localize(f"{wpm(self.engine.correct_chars, secs):.0f}"))
        else:
            self.wpm_v.setText(translator.localize("0"))
        self.acc_v.setText(translator.localize(f"{accuracy(self.engine.correct_keystrokes, self.engine.keystrokes) if self.engine and self.engine.keystrokes else 100:.0f}%"))
