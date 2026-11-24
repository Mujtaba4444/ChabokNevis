"""Central translation manager.

* Strings live in JSON files: app/i18n/locales/<code>.json  (flat "dotted.key": "text").
* Each file has a "_meta" block: code, name, native, rtl, digits, qt_locale, fonts, font_size.
* English (en) is the fallback for any key missing in another language.
* Adding a language = adding one JSON file (see README).
"""
from __future__ import annotations

import json
import logging
import re
import weakref

from PySide6.QtCore import QObject, Qt, Signal

from ..core.config import base_dir

log = logging.getLogger(__name__)

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
FALLBACK = "en"


class Translator(QObject):
    languageChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self._data: dict[str, dict[str, str]] = {}
        self._meta: dict[str, dict] = {}
        self._bindings: list = []
        self.code = FALLBACK
        self._load()

    # ---- loading -----------------------------------------------------------
    def _load(self):
        folder = base_dir() / "app" / "i18n" / "locales"
        for path in sorted(folder.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                meta = data.pop("_meta")
                self._meta[meta["code"]] = meta
                self._data[meta["code"]] = data
            except (OSError, ValueError, KeyError):
                log.exception("Could not load locale file %s", path)
        if FALLBACK not in self._data:
            self._data[FALLBACK], self._meta[FALLBACK] = {}, {"code": FALLBACK, "native": "English"}

    def available(self) -> list[tuple[str, str]]:
        """[(code, native name)] with English first."""
        codes = sorted(self._data, key=lambda c: (c != FALLBACK, c))
        return [(c, self._meta[c].get("native", c)) for c in codes]

    def has(self, code: str) -> bool:
        return code in self._data

    def meta(self, code: str | None = None) -> dict:
        return self._meta.get(code or self.code, self._meta[FALLBACK])

    # ---- state ---------------------------------------------------------------
    @property
    def is_rtl(self) -> bool:
        return bool(self.meta().get("rtl", False))

    def direction(self):
        return Qt.RightToLeft if self.is_rtl else Qt.LeftToRight

    def set_language(self, code: str) -> str:
        """Switch language (unknown codes fall back to English). Emits languageChanged."""
        if code not in self._data:
            code = FALLBACK
        changed = code != self.code
        self.code = code
        if changed:
            self.languageChanged.emit(code)
            self._apply_bindings()
        return code

    # ---- lookup --------------------------------------------------------------
    def tr(self, key: str, default: str | None = None, **kw) -> str:
        text = self._data.get(self.code, {}).get(key)
        if text is None:
            text = self._data[FALLBACK].get(key)
        if text is None:
            text = default if default is not None else key
        if kw:
            try:
                text = text.format(**kw)
            except (KeyError, IndexError, ValueError):
                log.warning("Bad placeholders for key %s", key)
        return self.localize(text)

    def localize(self, text) -> str:
        """Digits / decimal point / percent sign in the style of the current language."""
        text = str(text)
        if self.meta().get("digits") == "persian":
            text = _DECIMAL.sub("٫", text.translate(_PERSIAN_DIGITS)).replace("%", "٪")
        return text

    # ---- binding widgets so they follow language changes ----------------------
    def bind(self, widget, key: str, method: str = "setText", **kw):
        """Set widget.<method>(tr(key)) now and again whenever the language changes."""
        self._bindings.append((weakref.ref(widget), method, key, kw))
        self._apply_one(widget, method, key, kw)
        return widget

    def bind_combo(self, combo, key_fmt: str, items, defaults: dict | None = None):
        """Fill a QComboBox with `items` (data values) and translate item texts live."""
        for data in items:
            combo.addItem("", data)

        def apply():
            for i in range(combo.count()):
                d = combo.itemData(i)
                combo.setItemText(i, self.tr(key_fmt.format(d), default=(defaults or {}).get(d)))
        apply()
        self.languageChanged.connect(lambda _c: apply())

    def watch(self, fn):
        """Call fn() now and after every language change."""
        self.languageChanged.connect(lambda _c: fn())
        fn()

    def _apply_one(self, widget, method, key, kw):
        getattr(widget, method)(self.tr(key, **kw))

    def _apply_bindings(self):
        alive = []
        for ref, method, key, kw in self._bindings:
            w = ref()
            if w is None:
                continue
            try:
                self._apply_one(w, method, key, kw)
                alive.append((ref, method, key, kw))
            except RuntimeError:      # C++ widget already deleted
                continue
        self._bindings = alive


translator = Translator()
tr = translator.tr
