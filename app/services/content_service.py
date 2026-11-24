from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass

from ..core.config import content_path

LETTERS = "ابپتثجچحخدذرزسشصضطظعغفقکگلمنوهی"


@dataclass
class Lesson:
    key: str
    id: str
    level: int
    title: str
    intro: str
    variant: str
    difficulty: int = 1
    text: str = ""
    drill: str = ""
    length: int = 80


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


class ContentService:
    def __init__(self, settings):
        self.settings = settings
        self._rng = random.Random()
        self._lessons: dict[str, list[Lesson]] = {}
        self._pools: dict[str, dict] = {}

    @property
    def variant(self) -> str:
        return self.settings.get("content_variant")

    def lessons(self, variant=None) -> list[Lesson]:
        v = variant or self.variant
        if v not in self._lessons:
            items = (_read(content_path("shared", "lessons.json")) or []) + (_read(content_path(v, "lessons.json")) or [])
            out = [Lesson(key=f"{v}/{d['id']}", variant=v, id=d["id"], level=d["level"], title=d["title"],
                          intro=d.get("intro", ""), difficulty=d.get("difficulty", d["level"]),
                          text=d.get("text", ""), drill=d.get("drill", ""), length=d.get("length", 80)) for d in items]
            out.sort(key=lambda l: l.id)
            self._lessons[v] = out
        return self._lessons[v]

    def lesson_text(self, lesson: Lesson) -> str:
        return lesson.text or self.drill(lesson.drill, lesson.length)

    def drill(self, chars: str, length: int, max_group: int = 4) -> str:
        letters = [c for c in chars if not c.isspace()]
        out, n = [], 0
        while n < length:
            g = "".join(self._rng.choice(letters) for _ in range(self._rng.randint(2, max_group)))
            out.append(g)
            n += len(g) + 1
        return " ".join(out)

    def pool(self, category: str) -> list[str]:
        v = self.variant
        if v not in self._pools:
            merged: dict[str, list[str]] = {}
            for p in (content_path("shared", "pool.json"), content_path(v, "pool.json")):
                for k, items in (_read(p) or {}).items():
                    merged.setdefault(k, []).extend(items)
            self._pools[v] = merged
        return self._pools[v].get(category, [])

    def practice_text(self, category: str, difficulty: int = 1, min_chars: int = 200) -> str:
        if category == "characters":
            return self.drill(LETTERS, min_chars, 2 + difficulty)
        items = sorted(set(self.pool(category) or self.pool("sentences")), key=len)
        frac = {1: 0.4, 2: 0.7}.get(difficulty, 1.0)
        items = items[:max(3, math.ceil(len(items) * frac))]
        out, n, order = [], 0, []
        while n < min_chars:
            if not order:
                order = items[:]
                self._rng.shuffle(order)
            s = order.pop()
            out.append(s)
            n += len(s) + 1
        return " ".join(out)
