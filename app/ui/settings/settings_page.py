from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (QCheckBox, QComboBox, QFontComboBox, QFormLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QSpinBox, QVBoxLayout, QWidget)

from ...core.constants import VARIANTS
from ...i18n import translator
from ..widgets.common import Card, tlabel


class SettingsPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        s = ctx.settings
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("settings.title", "pageTitle"))
        card = Card()
        form = QFormLayout()
        card.box.addLayout(form)
        root.addWidget(card)
        root.addStretch()
        self._spins = []

        def combo(key, items, key_fmt, defaults=None):
            c = QComboBox()
            translator.bind_combo(c, key_fmt, items, defaults)
            c.setCurrentIndex(max(0, c.findData(s.get(key))))
            c.currentIndexChanged.connect(lambda _i, c=c: s.set(key, c.currentData()))
            return c

        def check(key, text_key, tip_key=None):
            c = QCheckBox()
            if tip_key:
                translator.bind(c, tip_key, "setToolTip")
            c.setChecked(bool(s.get(key)))
            c.toggled.connect(lambda v: s.set(key, v))
            return c

        def spin(key, lo, hi):
            c = QSpinBox(); c.setRange(lo, hi); c.setValue(int(s.get(key)))
            c.valueChanged.connect(lambda v: s.set(key, v))
            self._spins.append(c)
            return c

        def slider(key, lo, hi, step=1):
            c = QSlider(Qt.Horizontal)
            c.setRange(lo, hi)
            c.setSingleStep(step)
            c.setValue(int(s.get(key)))
            c.valueChanged.connect(lambda v: s.set(key, v))
            return c

        font = QFontComboBox()
        font.setWritingSystem(QFontDatabase.Arabic)
        font.setCurrentText(s.get("font_family"))
        font.currentFontChanged.connect(lambda f: s.set("font_family", f.family()))
        font.setEditable(False)

        lang = QComboBox()
        for code, native in translator.available():
            lang.addItem(native, code)
        lang.setCurrentIndex(max(0, lang.findData(s.get("ui_language"))))
        lang.currentIndexChanged.connect(lambda _i: s.set("ui_language", lang.currentData()))

        form.addRow(tlabel("settings.language"), lang)
        form.addRow(tlabel("settings.content"), combo("content_variant", list(VARIANTS), "variant.{}", VARIANTS))
        form.addRow(tlabel("settings.layout"), combo("keyboard_layout", list(ctx.layouts), "layout.{}", {k: l.name for k, l in ctx.layouts.items()}))
        form.addRow(tlabel("settings.theme"), combo("theme", ["light", "dark"], "theme.{}"))
        form.addRow(tlabel("settings.font"), font)
        form.addRow(tlabel("settings.font_size"), spin("font_size", 12, 48))
        form.addRow(tlabel("settings.goal"), spin("daily_goal_minutes", 1, 240))
        form.addRow(tlabel("settings.show_keyboard"), check("show_keyboard", "settings.show_keyboard"))

        # Typing Sounds section - only wrong-character sound
        sound_section = tlabel("settings.sound")
        sound_section.setObjectName("sectionTitle")
        form.addRow(sound_section)
        form.addRow(tlabel("settings.sound_tip"), check("sound", "settings.sound", "settings.sound_tip"))

        # Sound selection dropdown
        sound_combo = QComboBox()
        sound_combo.setMinimumWidth(200)
        self._sound_combo = sound_combo
        self._populate_sound_combo(s)
        translator.watch(lambda _c=None, s=s: self._populate_sound_combo(s))
        sound_combo.currentIndexChanged.connect(lambda _i: s.set("sound_index", self._sound_combo.currentData()))
        form.addRow(tlabel("settings.sound_select_tip"), sound_combo)

        # Preview button
        preview_btn = QPushButton()
        translator.bind(preview_btn, "settings.sound_preview")
        # Use minimum width to accommodate RTL text like "پیش‌نمایش"
        preview_btn.setMinimumWidth(100)
        preview_btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        preview_btn.clicked.connect(lambda: self._preview_sound())
        form.addRow(QLabel(), preview_btn)

        form.addRow(tlabel("settings.sound_volume"), slider("sound_volume", 0, 100))

        form.addRow(tlabel("settings.strict"), check("strict_mode", "settings.strict", "settings.strict_tip"))
        form.addRow(tlabel("settings.latin"), check("accept_latin", "settings.latin", "settings.latin_tip"))
        translator.watch(self._localize_spins)

    def _populate_sound_combo(self, s):
        from ...i18n import tr
        combo = self._sound_combo
        current = combo.currentData()
        combo.clear()
        for i in range(6):
            combo.addItem(tr(f"settings.sound_option.{i}"), i)
        idx = int(s.get("sound_index"))
        combo.setCurrentIndex(idx)

    def _preview_sound(self):
        """Preview the selected wrong-character sound using the shared sound service."""
        svc = self.ctx.sound_service
        svc.set_sound(int(self.ctx.settings.get("sound_index")))
        svc.set_volume(self.ctx.settings.get("sound_volume") / 100.0)
        svc.play_error()

    def _localize_spins(self):
        from PySide6.QtCore import QLocale
        for sp in self._spins:
            sp.setLocale(QLocale(translator.meta().get("qt_locale", "en_US")))