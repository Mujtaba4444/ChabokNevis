from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QCheckBox, QComboBox, QFontComboBox, QFormLayout, QSlider, QSpinBox, QVBoxLayout, QWidget

from ...core.constants import VARIANTS
from ...i18n import translator
from ..widgets.common import Card, tlabel


class SettingsPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
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
            c = QCheckBox()          # the row label (left) carries the text; the box itself stays empty
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
        # Make font family read-only (user selects from dropdown only)
        font.setEditable(False)

        lang = QComboBox()                      # language names are always shown in their own script
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

        # Typing Sounds section
        sound_section = tlabel("settings.sound")
        sound_section.setObjectName("sectionTitle")
        form.addRow(sound_section)
        form.addRow(tlabel("settings.sound_tip"), check("sound", "settings.sound", "settings.sound_tip"))
        form.addRow(tlabel("settings.sound_correct"), check("sound_correct", "settings.sound_correct"))
        form.addRow(tlabel("settings.sound_error"), check("sound_error", "settings.sound_error"))
        form.addRow(tlabel("settings.sound_volume"), slider("sound_volume", 0, 100))

        form.addRow(tlabel("settings.strict"), check("strict_mode", "settings.strict", "settings.strict_tip"))
        form.addRow(tlabel("settings.latin"), check("accept_latin", "settings.latin", "settings.latin_tip"))
        translator.watch(self._localize_spins)

    def _localize_spins(self):
        from PySide6.QtCore import QLocale
        for sp in self._spins:      # spin boxes show digits in the style of the current language
            sp.setLocale(QLocale(translator.meta().get("qt_locale", "en_US")))