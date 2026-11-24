from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

from ...i18n import tr, translator
from ..widgets.common import fmt_result, tlabel
from ..widgets.typing_panel import TypingPanel

CATEGORIES = ["characters", "words", "sentences", "paragraphs", "literature", "educational", "conversation", "custom"]


class PracticePage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        self.ctx = ctx
        self._saved = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("practice.title", "pageTitle"))
        bar = QHBoxLayout()
        self.cat, self.diff, self.dur = QComboBox(), QComboBox(), QComboBox()
        translator.bind_combo(self.cat, "practice.cat.{}", CATEGORIES)
        translator.bind_combo(self.diff, "practice.diff.{}", [1, 2, 3])
        translator.bind_combo(self.dur, "practice.dur.{}", [0, 60, 120, 180, 300])
        start = QPushButton(); translator.bind(start, "practice.start"); start.setObjectName("primary"); start.clicked.connect(self.start)
        fin = QPushButton(); translator.bind(fin, "practice.finish"); translator.bind(fin, "practice.finish_tip", "setToolTip")
        fin.clicked.connect(lambda: self.panel.finish())
        for w in (tlabel("practice.category"), self.cat, tlabel("practice.difficulty"), self.diff, tlabel("practice.duration"), self.dur, start, fin):
            bar.addWidget(w)
        bar.addStretch()
        root.addLayout(bar)
        self.custom = QPlainTextEdit()
        translator.bind(self.custom, "practice.custom_placeholder", "setPlaceholderText")
        self.custom.setLayoutDirection(Qt.RightToLeft)      # the text being typed is always Persian
        self.custom.setMaximumHeight(80)
        self.custom.hide()
        self.cat.currentIndexChanged.connect(lambda: self.custom.setVisible(self.cat.currentData() == "custom"))
        root.addWidget(self.custom)
        self.panel = TypingPanel(ctx)
        self.panel.finished.connect(self._done)
        root.addWidget(self.panel, 1)
        self.result = QLabel("")
        root.addWidget(self.result)
        translator.languageChanged.connect(lambda _c: self._show_saved())

    def start(self):
        cat, diff, dur = self.cat.currentData(), self.diff.currentData(), self.dur.currentData()
        self._saved = None
        self.result.setText("")
        if cat == "custom":
            text = " ".join(self.custom.toPlainText().split())
            if not text:
                box = QMessageBox(QMessageBox.Information, tr("practice.custom_title"), tr("practice.custom_empty"), QMessageBox.Ok, self)
                box.button(QMessageBox.Ok).setText(tr("common.ok"))
                box.exec()
                return
            self.panel.start(text)
            return
        gen = self.ctx.content.practice_text
        self.panel.start(gen(cat, diff, 250), duration=dur or None,
                         extender=(lambda: gen(cat, diff, 150)) if dur else None)

    def _done(self, res):
        self.ctx.progress.record_session("practice", self.ctx.content.variant, res)
        self._saved = res
        self._show_saved()

    def _show_saved(self):
        if self._saved:
            self.result.setText(tr("practice.saved", summary=fmt_result(self._saved)))

    def hideEvent(self, e):
        self.panel.stop()
        super().hideEvent(e)
