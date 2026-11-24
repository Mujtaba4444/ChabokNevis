from PySide6.QtWidgets import (QButtonGroup, QHBoxLayout, QHeaderView, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from ...core.constants import SPEED_TEST_DURATIONS
from ...i18n import tr, translator
from ..widgets.common import Card, fmt_duration, label, tlabel
from ..widgets.typing_panel import TypingPanel


class SpeedTestPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        self._last = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("speed.title", "pageTitle"))
        bar = QHBoxLayout()
        self.group = QButtonGroup(self)
        for i, (secs, _text) in enumerate(SPEED_TEST_DURATIONS):
            b = QPushButton(); translator.bind(b, f"speed.dur.{secs}"); b.setCheckable(True); b.setChecked(i == 1)
            self.group.addButton(b, secs); bar.addWidget(b)
        start = QPushButton(); translator.bind(start, "speed.start"); translator.bind(start, "speed.start_tip", "setToolTip")
        start.setObjectName("primary"); start.clicked.connect(self.start)
        bar.addWidget(start); bar.addStretch()
        root.addLayout(bar)
        self.panel = TypingPanel(ctx)
        self.panel.finished.connect(self._done)
        root.addWidget(self.panel, 1)
        self.result = Card()
        self.result_lbl = label("", "sectionTitle")
        self.detail = label("", "muted")
        self.result.box.addWidget(self.result_lbl); self.result.box.addWidget(self.detail)
        self.result.hide()
        root.addWidget(self.result)
        self.empty = tlabel("speed.no_results", "muted")
        root.addWidget(self.empty)
        self.table = QTableWidget(0, 5)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMaximumHeight(170)
        root.addWidget(self.table)
        translator.watch(self._retranslate)

    def _retranslate(self):
        self.table.setHorizontalHeaderLabels([tr(f"speed.col.{k}") for k in ("date", "duration", "wpm", "accuracy", "chars")])
        self._show_result()
        self.refresh()

    def refresh(self):
        rows = self.ctx.progress.sessions.recent(10, "speed_test")
        self.table.setRowCount(len(rows))
        self.table.setVisible(bool(rows))
        self.empty.setVisible(not rows)
        for i, r in enumerate(rows):
            vals = [r["created_at"][:16].replace("T", " "), fmt_duration(r["duration"]), f"{r['wpm']:.1f}",
                    f"{r['accuracy']:.1f}%", str(r["correct_characters"] + r["incorrect_characters"])]
            for j, v in enumerate(vals):
                self.table.setItem(i, j, QTableWidgetItem(translator.localize(v)))

    def start(self):
        secs = self.group.checkedId()
        gen = self.ctx.content.practice_text
        self._last = None
        self.result.hide()
        self.panel.start(gen("sentences", 2, 300), duration=secs, extender=lambda: gen("sentences", 2, 150))

    def _done(self, res):
        self.ctx.progress.record_session("speed_test", self.ctx.content.variant, res)
        self._last = res
        self._show_result()
        self.refresh()

    def _show_result(self):
        res = self._last
        if not res:
            return
        self.result_lbl.setText(tr("speed.result", wpm=f"{res['wpm']:.1f}", acc=f"{res['accuracy']:.1f}"))
        self.detail.setText(tr("speed.detail", c=res["correct_characters"], i=res["incorrect_characters"],
                               t=res["total_characters"], d=fmt_duration(res["duration"])))
        self.result.show()

    def hideEvent(self, e):
        self.panel.stop()
        super().hideEvent(e)
