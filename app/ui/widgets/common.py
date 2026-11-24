from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from ...i18n import tr, translator


class Card(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(18, 14, 18, 14)


class StatCard(Card):
    def __init__(self, title_key: str, value: str = "-"):
        super().__init__()
        t = QLabel()
        translator.bind(t, title_key)
        t.setObjectName("muted")
        self.value = QLabel(value)
        self.value.setObjectName("cardValue")
        self.box.addWidget(t)
        self.box.addWidget(self.value)

    def set_value(self, v: str):
        self.value.setText(v)


def label(text: str, name: str = "") -> QLabel:
    l = QLabel(text)
    if name:
        l.setObjectName(name)
    return l


def tlabel(key: str, name: str = "", **kw) -> QLabel:
    """A QLabel whose text follows the interface language."""
    l = QLabel()
    if name:
        l.setObjectName(name)
    translator.bind(l, key, **kw)
    return l


def fmt_duration(seconds: float) -> str:
    s = int(seconds)
    h, m, sec = s // 3600, s % 3600 // 60, s % 60
    if h:
        return tr("time.hm", h=h, m=m)
    return tr("time.ms", m=m, s=sec) if m else tr("time.s", s=sec)


def fmt_result(res: dict) -> str:
    return tr("result.summary", wpm=f"{res['wpm']:.1f}", acc=f"{res['accuracy']:.1f}",
              chars=res["total_characters"], time=fmt_duration(res["duration"]))


def lesson_title(lesson) -> str:
    return tr(f"lesson.{lesson.id}.title", default=lesson.title)


def lesson_intro(lesson) -> str:
    return tr(f"lesson.{lesson.id}.intro", default=lesson.intro)


def lesson_code(lesson) -> str:
    return tr("lesson.code", id=lesson.id, level=lesson.level, num=lesson.id.rsplit("-", 1)[-1])
