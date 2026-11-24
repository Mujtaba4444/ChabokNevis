from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ...i18n import tr, translator
from .. import theme


class _Chart(QWidget):
    def __init__(self, title="", unit=""):
        super().__init__()
        self.title, self.unit, self.values, self.labels = title, unit, [], []
        self.setMinimumHeight(190)

    def set_data(self, values, labels=None):
        self.values, self.labels = list(values), list(labels or [])
        self.update()

    def _frame(self, p):
        c = theme.colors()
        p.setPen(QColor(c["text"]))
        p.drawText(QRectF(8, 4, self.width() - 16, 22), (Qt.AlignRight if translator.is_rtl else Qt.AlignLeft) | Qt.AlignVCenter, self.title)
        plot = QRectF(40, 34, self.width() - 56, self.height() - 64)
        if not self.values or max(self.values) <= 0:
            p.setPen(QColor(c["muted"]))
            p.drawText(plot, Qt.AlignCenter, tr("chart.no_data"))
            return None, c
        top = max(self.values) * 1.15
        p.setPen(QPen(QColor(c["border"]), 1))
        p.drawLine(plot.bottomLeft(), plot.bottomRight())
        p.drawLine(plot.topLeft(), plot.bottomLeft())
        p.setPen(QColor(c["muted"]))
        p.drawText(QRectF(0, plot.top() - 8, 38, 16), Qt.AlignRight | Qt.AlignVCenter, translator.localize(f"{top:.0f}"))
        p.drawText(QRectF(0, plot.bottom() - 8, 38, 16), Qt.AlignRight | Qt.AlignVCenter, translator.localize("0"))
        return (plot, top), c


class LineChart(_Chart):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        frame, c = self._frame(p)
        if not frame:
            return
        plot, top = frame
        n = len(self.values)
        pts = [QPointF(plot.left() + (plot.width() * i / max(n - 1, 1) if n > 1 else plot.width() / 2),
                       plot.bottom() - plot.height() * v / top) for i, v in enumerate(self.values)]
        path = QPainterPath(pts[0])
        for pt in pts[1:]:
            path.lineTo(pt)
        p.setPen(QPen(QColor(c["secondary"]), 2.5))
        p.drawPath(path)
        p.setBrush(QColor(c["primary"]))
        for pt in pts:
            p.drawEllipse(pt, 3.5, 3.5)


class BarChart(_Chart):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        frame, c = self._frame(p)
        if not frame:
            return
        plot, top = frame
        n = len(self.values)
        slot = plot.width() / n
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(c["secondary"]))
        for i, v in enumerate(self.values):
            h = plot.height() * v / top
            p.drawRoundedRect(QRectF(plot.left() + i * slot + slot * 0.15, plot.bottom() - h, slot * 0.7, h), 3, 3)
        p.setPen(QColor(c["muted"]))
        for i in (0, n // 2, n - 1):
            if i < len(self.labels):
                p.drawText(QRectF(plot.left() + i * slot - 20, plot.bottom() + 4, slot + 40, 16), Qt.AlignCenter, translator.localize(self.labels[i]))
