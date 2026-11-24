"""Physical keyboard layouts (loaded from content/layouts/*.json)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from ..engine.text_normalizer import normalize_char
from .config import content_path

_US_BASE = "`1234567890-=[]\\;',./"
_US_SHIFT = '~!@#$%^&*()_+{}|:"<>?'
_SHIFT_OF = dict(zip(_US_BASE, _US_SHIFT))

_FINGER_KEYS = {
    "L5": "`1qaz", "L4": "2wsx", "L3": "3edc", "L2": "45rtfgvb",
    "R2": "67yuhjnm", "R3": "8ik,", "R4": "9ol.", "R5": "0-=p[]\\;'/",
}
FINGER_OF = {k: f for f, keys in _FINGER_KEYS.items() for k in keys}


@dataclass(frozen=True)
class Key:
    latin: str        # label of the physical (US) key
    base: str         # character produced without Shift
    shift: str        # character produced with Shift
    row: int
    col: int
    finger: str
    shift_latin: str


class Layout:
    def __init__(self, layout_id: str, name: str, rows: list[list[list[str]]]):
        self.id, self.name = layout_id, name
        self.keys: list[Key] = []
        self._by_char: dict[str, tuple[Key, bool]] = {}
        self._from_latin: dict[str, str] = {}
        self._punct: set[str] = set()
        for r, row in enumerate(rows):
            for c, (latin, base, shift) in enumerate(row):
                sl = latin.upper() if latin.isalpha() else _SHIFT_OF.get(latin, "")
                key = Key(latin, base, shift, r, c, FINGER_OF.get(latin, "R5"), sl)
                self.keys.append(key)
                if base:
                    self._by_char.setdefault(normalize_char(base), (key, False))
                    self._from_latin[latin] = base
                    if not base.isascii() and not latin.isalnum():
                        self._punct.add(latin)
                if shift:
                    self._by_char.setdefault(normalize_char(shift), (key, True))
                    if sl:
                        self._from_latin[sl] = shift
                        if not shift.isascii() and not sl.isalnum():
                            self._punct.add(sl)

    def locate(self, ch: str) -> tuple[Key, bool] | None:
        """Return (key, needs_shift) for a Persian character."""
        return self._by_char.get(normalize_char(ch))

    def map_input(self, ch: str) -> str:
        """Translate a character produced by an English OS layout into the Persian
        character on the same physical key. Characters that are already Persian
        (OS Persian layout) and ASCII punctuation shared by both layouts pass through."""
        if len(ch) != 1 or not ch.isascii():
            return ch
        if ch.isalnum() or ch in self._punct:
            return self._from_latin.get(ch, ch)
        return ch


def load_layouts() -> dict[str, Layout]:
    layouts: dict[str, Layout] = {}
    for path in sorted(content_path("layouts").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        layouts[data["id"]] = Layout(data["id"], data["name"], data["rows"])
    return layouts
