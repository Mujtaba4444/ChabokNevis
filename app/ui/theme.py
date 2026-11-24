from string import Template

LIGHT = dict(name="light", primary="#1E3A8A", secondary="#14B8A6", bg="#EEF1F5", card="#FFFFFF", text="#0F1B3D",
             muted="#6B7794", border="#DDE2EB", success="#16A34A", error="#DC2626", sidebar="#1E3A8A",
             sidebar_text="#E6ECFF", success_bg="#DCFCE7", error_bg="#FEE2E2", cur_bg="#CCFBF1", key="#FFFFFF")
DARK = dict(name="dark", primary="#3B82F6", secondary="#2DD4BF", bg="#0E1424", card="#18203A", text="#E6EAF5",
            muted="#8E99B8", border="#2A3556", success="#4ADE80", error="#F87171", sidebar="#0A1020",
            sidebar_text="#C9D3F0", success_bg="#14532D", error_bg="#7F1D1D", cur_bg="#134E4A", key="#232C4B")

_current = LIGHT


def set_theme(name: str):
    global _current
    _current = DARK if name == "dark" else LIGHT


def colors() -> dict:
    return _current


_QSS = Template("""
QWidget { color: $text; }
QMainWindow, QWidget#page, QScrollArea, QScrollArea > QWidget > QWidget { background: $bg; }
QWidget#sidebar { background: $sidebar; }
QLabel#brand { color: white; font-size: 20px; font-weight: 700; padding: 18px 16px; background: transparent; }
QPushButton#nav { color: $sidebar_text; background: transparent; border: none; text-align: $nav_align;
  padding: 11px 18px; border-radius: 8px; margin: 2px 10px; }
QPushButton#nav:hover { background: rgba(255,255,255,0.09); }
QPushButton#nav:checked { background: $secondary; color: #06201C; font-weight: 600; }
QLabel#pageTitle { font-size: 26px; font-weight: 700; background: transparent; }
QLabel#sectionTitle { font-size: 16px; font-weight: 600; background: transparent; }
QLabel#muted { color: $muted; background: transparent; }
QLabel#cardValue { font-size: 26px; font-weight: 700; color: $primary; background: transparent; }
QLabel { background: transparent; }
QFrame#card { background: $card; border: 1px solid $border; border-radius: 12px; }
QPushButton { background: $card; border: 1px solid $border; border-radius: 8px; padding: 8px 16px; }
QPushButton:hover { border-color: $secondary; }
QPushButton:checked { background: $secondary; color: #06201C; border-color: $secondary; }
QPushButton:disabled { color: $muted; }
QPushButton#primary { background: $primary; color: white; border: none; font-weight: 600; }
QPushButton#primary:hover { background: $secondary; color: #06201C; }
QPlainTextEdit#typingArea { background: $card; border: 1px solid $border; border-radius: 12px; padding: 14px; color: $text; }
QPlainTextEdit, QLineEdit, QComboBox, QSpinBox, QFontComboBox { background: $card; border: 1px solid $border; border-radius: 6px; padding: 4px 8px; }
QComboBox QAbstractItemView { background: $card; color: $text; selection-background-color: $secondary; }
QProgressBar { background: $border; border: none; border-radius: 5px; height: 10px; text-align: center; color: transparent; }
QProgressBar::chunk { background: $secondary; border-radius: 5px; }
QTableWidget { background: $card; border: 1px solid $border; gridline-color: $border; }
QHeaderView::section { background: $bg; border: none; padding: 6px; font-weight: 600; }
QCheckBox {
    background: transparent;
    spacing: 10px;
    min-width: 20px;
    min-height: 20px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border: 2px solid $border;
    border-radius: 4px;
    background: $card;
}
QCheckBox::indicator:hover {
    border-color: $secondary;
    background: $bg;
}
QCheckBox::indicator:checked {
    background: $primary;
    border-color: $primary;
}
QCheckBox::indicator:checked:hover {
    background: $secondary;
    border-color: $secondary;
}
QScrollArea#statsScroll {
    border: none;
    background: transparent;
}
QScrollArea#statsScroll QScrollBar:vertical {
    border: none;
    background: $border;
    width: 12px;
    margin: 0;
}
QScrollArea#statsScroll QScrollBar::handle:vertical {
    background: $muted;
    min-height: 30px;
    border-radius: 6px;
}
QScrollArea#statsScroll QScrollBar::handle:vertical:hover {
    background: $secondary;
}
QLineEdit#fontSelector, QFontComboBox {
    padding-right: 28px;
}
QLineEdit#fontSelector:focus, QFontComboBox:focus {
    border-color: $primary;
}
""")


def stylesheet(rtl: bool = False) -> str:
    return _QSS.substitute(_current, nav_align="right" if rtl else "left")
