from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..core.constants import APP_NAME, APP_VERSION
from ..i18n import tr, translator
from .widgets.common import Card, label, tlabel


class AboutPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("about.title", "pageTitle"))
        card = Card()
        self.name = label("", "sectionTitle")
        card.box.addWidget(self.name)
        card.box.addWidget(tlabel("about.desc", "muted"))
        card.box.addWidget(tlabel("about.shortcuts", "muted"))
        root.addWidget(card)
        root.addStretch()
        translator.watch(lambda: self.name.setText(tr("about.name", app=tr("app.title"), ver=APP_VERSION)))
