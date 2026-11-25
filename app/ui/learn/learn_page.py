from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget)

from ...core.constants import LESSON_PASS_ACCURACY
from ...i18n import tr, translator
from ..widgets.common import Card, fmt_result, label, lesson_code, lesson_intro, lesson_title, tlabel
from ..widgets.typing_panel import TypingPanel


class LessonView(QWidget):
    def __init__(self, ctx, on_back, on_next):
        super().__init__()
        self.ctx, self.lesson, self.on_next = ctx, None, on_next
        self._outcome = None            # (passed, result) of the last finished attempt

        # Use a scroll area to ensure all content is accessible in constrained windows
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)  # Reduced spacing for better responsiveness

        top = QHBoxLayout()
        back = QPushButton()
        translator.bind(back, "learn.back")
        back.clicked.connect(on_back)
        self.title = label("", "pageTitle")
        top.addWidget(back); top.addWidget(self.title, 1)
        root.addLayout(top)

        self.intro = label("", "muted")
        self.intro.setWordWrap(True)
        root.addWidget(self.intro)

        self.panel = TypingPanel(ctx)
        self.panel.finished.connect(self._done)
        root.addWidget(self.panel, 1)

        row = QHBoxLayout()
        self.result = QLabel("")
        restart = QPushButton()
        translator.bind(restart, "learn.restart")
        translator.bind(restart, "learn.restart_tip", "setToolTip")
        restart.clicked.connect(self.restart)
        self.next_btn = QPushButton()
        translator.bind(self.next_btn, "learn.next")
        self.next_btn.setObjectName("primary")
        self.next_btn.clicked.connect(lambda: self.on_next(self.lesson))
        self.next_btn.hide()
        row.addWidget(self.result, 1); row.addWidget(restart); row.addWidget(self.next_btn)
        root.addLayout(row)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        translator.languageChanged.connect(lambda _c: self._retranslate())

    def open(self, lesson):
        self.lesson = lesson
        self._retranslate()
        self.restart()

    def restart(self):
        self._outcome = None
        self.result.setText("")
        self.next_btn.hide()
        self.panel.start(self.ctx.content.lesson_text(self.lesson))

    def _retranslate(self):
        if self.lesson:
            self.title.setText(f"{lesson_code(self.lesson)}  {lesson_title(self.lesson)}")
            self.intro.setText(lesson_intro(self.lesson))
        self._show_outcome()

    def _show_outcome(self):
        if not self._outcome:
            return
        passed, res = self._outcome
        if passed:
            self.result.setText(tr("learn.complete", summary=fmt_result(res)))
        else:
            self.result.setText(tr("learn.failed", n=f"{LESSON_PASS_ACCURACY:.0f}", summary=fmt_result(res)))

    def _done(self, res):
        passed = res["completed_text"] and res["accuracy"] >= LESSON_PASS_ACCURACY
        self.ctx.progress.record_session("lesson", self.ctx.content.variant, res, self.lesson.key, passed)
        self._outcome = (passed, res)
        self._show_outcome()
        if passed:
            self.next_btn.show()


class LearnPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        self.stack = QStackedWidget()
        root.addWidget(self.stack)
        listing = QWidget()
        lv = QVBoxLayout(listing)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.addWidget(tlabel("learn.title", "pageTitle"))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        self.body = QWidget()
        self.body_l = QVBoxLayout(self.body)
        scroll.setWidget(self.body)
        lv.addWidget(scroll)
        self.view = LessonView(ctx, self.show_list, self.next_lesson)
        self.stack.addWidget(listing)
        self.stack.addWidget(self.view)
        ctx.settings.changed.connect(lambda k: self.refresh() if k == "content_variant" else None)
        translator.languageChanged.connect(lambda _c: self._rebuild())

    def show_list(self):
        self.view.panel.stop()
        self.stack.setCurrentIndex(0)
        self.refresh()

    def refresh(self):
        if self.stack.currentIndex() == 1:
            return
        self._rebuild()

    def _rebuild(self):
        while self.body_l.count():
            it = self.body_l.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        done, prog = self.ctx.progress.completed_keys(), self.ctx.progress.lessons.progress()
        lessons = self.ctx.content.lessons()
        nxt = next((l for l in lessons if l.key not in done), None)
        level = 0
        for l in lessons:
            if l.level != level:
                level = l.level
                self.body_l.addWidget(label(tr("learn.level_header", n=level, name=tr(f"level.{level}")), "sectionTitle"))
            card = Card()
            row = QHBoxLayout()
            mark = "✅" if l.key in done else ("▶" if l is nxt else "○")
            row.addWidget(QLabel(f"{mark}  {lesson_code(l)}   {lesson_title(l)}"), 1)
            p = prog.get(l.key)
            row.addWidget(label(tr("learn.best", wpm=f"{p['best_wpm']:.0f}", acc=f"{p['best_accuracy']:.0f}") if p else "", "muted"))
            b = QPushButton(tr("learn.repeat") if l.key in done else tr("learn.start"))
            b.clicked.connect(lambda _=False, les=l: self.open(les))
            row.addWidget(b)
            card.box.addLayout(row)
            self.body_l.addWidget(card)
        self.body_l.addStretch()

    def open(self, lesson):
        self.stack.setCurrentIndex(1)
        self.view.open(lesson)

    def next_lesson(self, current):
        lessons = self.ctx.content.lessons()
        idx = lessons.index(current) if current in lessons else -1
        if idx + 1 < len(lessons):
            self.open(lessons[idx + 1])
        else:
            self.show_list()
