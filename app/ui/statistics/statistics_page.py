from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from ...i18n import tr, translator
from ..widgets.charts import BarChart, LineChart
from ..widgets.common import Card, StatCard, fmt_duration, tlabel


class StatisticsPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("stats.title", "pageTitle"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setObjectName("statsScroll")
        root.addWidget(scroll, 1)

        content = QWidget()
        content.setObjectName("statsContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        grid = QGridLayout()
        self.cards = {k: StatCard(f"stats.{k}") for k in ("total_time", "lessons", "avg_wpm", "best_wpm", "avg_acc", "week_month")}
        for i, c in enumerate(self.cards.values()):
            grid.addWidget(c, i // 3, i % 3)
        layout.addLayout(grid)

        self.wpm_chart = LineChart()
        self.day_chart = BarChart()
        for ch in (self.wpm_chart, self.day_chart):
            card = Card(); card.box.addWidget(ch); layout.addWidget(card)
        layout.addStretch()
        scroll.setWidget(content)

        translator.watch(self.refresh)

    def refresh(self):
        p = self.ctx.progress
        s = p.summary()
        c = self.cards
        c["total_time"].set_value(fmt_duration(s["total_seconds"]))
        c["lessons"].set_value(translator.localize(len(p.completed_keys())))
        c["avg_wpm"].set_value(translator.localize(f"{s['avg_wpm']:.1f}"))
        c["best_wpm"].set_value(translator.localize(f"{s['best_wpm']:.1f}"))
        c["avg_acc"].set_value(translator.localize(f"{s['avg_accuracy']:.1f}%"))
        month = p.daily.last_days(30)
        c["week_month"].set_value(tr("stats.week_month_value", w=f"{sum(v for _, v in month[-7:]) / 60:.0f}", m=f"{sum(v for _, v in month) / 60:.0f}"))
        self.wpm_chart.title = tr("stats.chart_wpm")
        self.day_chart.title = tr("stats.chart_days")
        self.wpm_chart.set_data([r["wpm"] for r in reversed(p.sessions.recent(30))])
        days = p.daily.last_days(14)
        self.day_chart.set_data([v / 60 for _, v in days], [d[5:] for d, _ in days])
