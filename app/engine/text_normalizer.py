"""Persian text normalisation (configurable)."""
from __future__ import annotations

from dataclasses import dataclass

ZWNJ = "\u200c"
PERSIAN_YEH, ARABIC_YEH, ALEF_MAKSURA = "\u06cc", "\u064a", "\u0649"
PERSIAN_KAF, ARABIC_KAF = "\u06a9", "\u0643"

_LETTERS = {ARABIC_YEH: PERSIAN_YEH, ALEF_MAKSURA: PERSIAN_YEH, ARABIC_KAF: PERSIAN_KAF}
_DIGITS: dict[str, str] = {}
for _i in range(10):
    _DIGITS[chr(0x0660 + _i)] = chr(0x06F0 + _i)  # Arabic-Indic -> Persian
    _DIGITS[str(_i)] = chr(0x06F0 + _i)           # Latin -> Persian
DIACRITICS = frozenset(chr(c) for c in range(0x064B, 0x0660)) | {"\u0670"}


@dataclass(frozen=True)
class NormalizationRules:
    unify_letters: bool = True      # Arabic yeh/kaf == Persian yeh/kaf
    unify_digits: bool = True       # Latin / Arabic-Indic / Persian digits are equal
    strip_diacritics: bool = False  # ignore diacritics in the target text
    zwnj_as_space: bool = False     # accept a space where ZWNJ is expected


RELAXED = NormalizationRules()  # used for performance measurement
STRICT = NormalizationRules(False, False, False, False)  # exact keyboard-layout training


def normalize_char(ch: str, rules: NormalizationRules = RELAXED) -> str:
    if rules.unify_letters:
        ch = _LETTERS.get(ch, ch)
    if rules.unify_digits:
        ch = _DIGITS.get(ch, ch)
    if rules.zwnj_as_space and ch == ZWNJ:
        ch = " "
    return ch


def normalize(text: str, rules: NormalizationRules = RELAXED) -> str:
    out = []
    for ch in text:
        if rules.strip_diacritics and ch in DIACRITICS:
            continue
        out.append(normalize_char(ch, rules))
    return "".join(out)


def chars_match(expected: str, typed: str, rules: NormalizationRules = RELAXED) -> bool:
    return normalize_char(expected, rules) == normalize_char(typed, rules)
