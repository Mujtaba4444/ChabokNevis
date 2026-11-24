from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..widgets.common import Card, tlabel


class GamesPage(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.setObjectName("page")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.addWidget(tlabel("games.title", "pageTitle"))
        card = Card()
        card.box.addWidget(tlabel("games.coming", "sectionTitle"))
        for key in ("games.word", "games.time", "games.accuracy"):
            card.box.addWidget(tlabel(key, "muted"))
        root.addWidget(card)
        root.addStretch()
