from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget

from ...i18n import tr, translator
from ..widgets.common import Card, StatCard, fmt_duration, label, lesson_title, tlabel


class DashboardPage(QWidget):
    navigate = Signal(str)

    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("dashboard.welcome", "pageTitle"))
        self.sub = label("", "muted")
        root.addWidget(self.sub)
        grid = QGridLayout()
        self.level = StatCard("dashboard.level")
        self.progress = StatCard("dashboard.progress")
        self.total = StatCard("dashboard.total_time")
        self.avg = StatCard("dashboard.avg_speed")
        self.acc = StatCard("dashboard.accuracy")
        goal = Card()
        goal.box.addWidget(tlabel("dashboard.goal", "muted"))
        self.goal_v = label("-", "cardValue")
        self.goal_bar = QProgressBar()
        self.goal_bar.setRange(0, 100)
        goal.box.addWidget(self.goal_v)
        goal.box.addWidget(self.goal_bar)
        for i, w in enumerate([self.level, self.progress, goal, self.total, self.avg, self.acc]):
            grid.addWidget(w, i // 3, i % 3)
        root.addLayout(grid)
        self.recent = Card()
        self.recent.box.addWidget(tlabel("dashboard.recent", "sectionTitle"))
        self.recent_list = QVBoxLayout()
        self.recent.box.addLayout(self.recent_list)
        root.addWidget(self.recent)
        row = QHBoxLayout()
        for key, text_key in (("learn", "dashboard.continue"), ("practice", "dashboard.free_practice"), ("speed_test", "dashboard.speed_test")):
            b = QPushButton()
            translator.bind(b, text_key)
            b.setObjectName("primary" if key == "learn" else "")
            b.clicked.connect(lambda _=False, k=key: self.navigate.emit(k))
            row.addWidget(b)
        row.addStretch()
        root.addLayout(row)
        root.addStretch()
        translator.languageChanged.connect(lambda _c: self.refresh())   # dynamic texts follow the language

    def refresh(self):
        c = self.ctx
        s = c.progress.summary()
        lessons = c.content.lessons()
        done = c.progress.completed_keys()
        nxt = next((l for l in lessons if l.key not in done), None)
        self.level.set_value(tr(f"level.{(nxt or lessons[-1]).level}"))
        self.progress.set_value(translator.localize(f"{len(done & {l.key for l in lessons}) * 100 // max(len(lessons), 1)}%"))
        goal = int(c.settings.get("daily_goal_minutes"))
        today = s["today_seconds"] / 60
        self.goal_v.setText(tr("dashboard.goal_value", done=f"{today:.0f}", goal=goal))
        self.goal_bar.setValue(min(100, int(today * 100 / max(goal, 1))))
        self.total.set_value(fmt_duration(s["total_seconds"]))
        self.avg.set_value(tr("dashboard.avg_speed_value", wpm=f"{s['avg_wpm']:.0f}"))
        self.acc.set_value(translator.localize(f"{s['avg_accuracy']:.0f}%"))
        self.sub.setText(tr("dashboard.next_lesson", title=lesson_title(nxt)) if nxt else tr("dashboard.all_done"))
        while self.recent_list.count():
            w = self.recent_list.takeAt(0).widget()
            if w:
                w.deleteLater()
        rows = c.progress.sessions.recent(5)
        if not rows:
            self.recent_list.addWidget(label(tr("dashboard.no_activity"), "muted"))
        for r in rows:
            self.recent_list.addWidget(QLabel(tr("dashboard.activity_row", date=r["created_at"][:16].replace("T", " "),
                                                 kind=tr(f"session.{r['session_type']}"), wpm=f"{r['wpm']:.0f}", acc=f"{r['accuracy']:.0f}")))
