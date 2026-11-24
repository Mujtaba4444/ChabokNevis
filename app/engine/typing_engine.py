"""Real-time comparison of typed input against a target text (UI independent)."""
from __future__ import annotations

from enum import Enum

from .statistics_engine import accuracy, wpm
from .text_normalizer import RELAXED, NormalizationRules, chars_match, normalize


class CharState(Enum):
    PENDING = 0
    CORRECT = 1
    INCORRECT = 2
    CURRENT = 3


class TypingEngine:
    def __init__(self, target: str, rules: NormalizationRules = RELAXED):
        self.rules = rules
        self.target = normalize(target, rules) if rules.strip_diacritics else target
        self._ok: list[bool] = []
        self.keystrokes = 0
        self.correct_keystrokes = 0
        self.incorrect_keystrokes = 0

    @property
    def position(self) -> int:
        return len(self._ok)

    @property
    def finished(self) -> bool:
        return self.position >= len(self.target)

    @property
    def expected(self) -> str | None:
        return None if self.finished else self.target[self.position]

    @property
    def correct_chars(self) -> int:
        """Characters that are correct in the text as it currently stands."""
        return sum(self._ok)

    def type_char(self, ch: str) -> bool | None:
        """Register a typed character. Returns True/False, or None if already finished."""
        if self.finished:
            return None
        ok = chars_match(self.target[self.position], ch, self.rules)
        self._ok.append(ok)
        self.keystrokes += 1
        if ok:
            self.correct_keystrokes += 1
        else:
            self.incorrect_keystrokes += 1
        return ok

    def backspace(self) -> bool:
        if not self._ok:
            return False
        self._ok.pop()
        return True

    def extend(self, more: str) -> None:
        self.target += normalize(more, self.rules) if self.rules.strip_diacritics else more

    def states(self) -> list[CharState]:
        out = [CharState.CORRECT if ok else CharState.INCORRECT for ok in self._ok]
        if not self.finished:
            out.append(CharState.CURRENT)
        out.extend([CharState.PENDING] * (len(self.target) - len(out)))
        return out

    def result(self, seconds: float) -> dict:
        """Accuracy uses keystrokes (so corrected mistakes still count);
        WPM uses the correct characters left in the final text (net speed)."""
        return {
            "wpm": wpm(self.correct_chars, seconds),
            "accuracy": accuracy(self.correct_keystrokes, self.keystrokes),
            "correct_characters": self.correct_keystrokes,
            "incorrect_characters": self.incorrect_keystrokes,
            "total_characters": self.keystrokes,
            "duration": seconds,
        }
