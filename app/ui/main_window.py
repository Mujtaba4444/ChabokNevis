from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from ..core.constants import DEFAULT_LANGUAGE, NAV_ITEMS
from ..i18n import translator
from ..services.context import build_context
from . import theme
from .about_page import AboutPage
from .dashboard.dashboard_page import DashboardPage
from .games.games_page import GamesPage
from .learn.learn_page import LearnPage
from .practice.practice_page import PracticePage
from .settings.settings_page import SettingsPage
from .speed_test.speed_test_page import SpeedTestPage
from .statistics.statistics_page import StatisticsPage
from .widgets.common import tlabel


class MainWindow(QMainWindow):
    def __init__(self, ctx=None):
        super().__init__()
        self.ctx = ctx or build_context()
        self.resize(1180, 820)                      # size used when the window is restored from maximized
        saved = self.ctx.settings.get("ui_language")
        translator.set_language(saved if translator.has(saved) else DEFAULT_LANGUAGE)   # saved choice, Dari by default
        self._apply_style()
        # connected before any page, so direction/fonts are updated before the pages re-translate
        translator.languageChanged.connect(lambda _c: self._apply_style())
        self.ctx.settings.changed.connect(self._on_setting)
        translator.bind(self, "app.title", "setWindowTitle")

        central = QWidget()
        self.setCentralWidget(central)
        row = QHBoxLayout(central)                  # in RTL Qt mirrors this row: the sidebar moves to the right
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        side = QWidget(); side.setObjectName("sidebar"); side.setFixedWidth(220)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 0, 0, 12)
        sl.addWidget(tlabel("app.brand", "brand"))
        self.group = QButtonGroup(self)
        self.stack = QStackedWidget()
        self.pages = {}
        factories = {"dashboard": DashboardPage, "learn": LearnPage, "practice": PracticePage, "speed_test": SpeedTestPage,
                     "games": GamesPage, "statistics": StatisticsPage, "settings": SettingsPage, "about": AboutPage}
        for i, (key, _title) in enumerate(NAV_ITEMS):
            page = factories[key](self.ctx)
            self.pages[key] = page
            self.stack.addWidget(page)
            b = QPushButton(); b.setObjectName("nav"); b.setCheckable(True)
            translator.bind(b, f"nav.{key}")
            b.clicked.connect(lambda _=False, k=key: self.navigate(k))
            self.group.addButton(b, i); sl.addWidget(b)
        sl.addStretch()
        self.pages["dashboard"].navigate.connect(self.navigate)
        row.addWidget(side)
        row.addWidget(self.stack, 1)
        self.navigate("dashboard")
        QShortcut(QKeySequence(Qt.Key_F11), self, activated=self._toggle_fullscreen)

    # ---- navigation ------------------------------------------------------------
    def navigate(self, key: str):
        keys = [k for k, _ in NAV_ITEMS]
        i = keys.index(key)
        self.group.button(i).setChecked(True)
        self.stack.setCurrentIndex(i)
        page = self.pages[key]
        if hasattr(page, "refresh"):
            page.refresh()

    def _toggle_fullscreen(self):
        self.showMaximized() if self.isFullScreen() else self.showFullScreen()

    # ---- settings / language / style ---------------------------------------------
    def _on_setting(self, key: str):
        if key == "theme":
            self._apply_style()
        elif key == "ui_language":
            saved = self.ctx.settings.get("ui_language")
            translator.set_language(saved if translator.has(saved) else DEFAULT_LANGUAGE)

    def _apply_style(self):
        """Theme + language dependent look: layout direction, locale, fonts, stylesheet."""
        theme.set_theme(self.ctx.settings.get("theme"))
        meta = translator.meta()
        app = QApplication.instance()
        app.setLayoutDirection(translator.direction())          # Qt.RightToLeft mirrors every layout
        QLocale.setDefault(QLocale(meta.get("qt_locale", "en_US")))
        f = QFont()
        f.setFamilies(meta.get("fonts", ["Segoe UI", "Tahoma"]))
        f.setPointSize(int(meta.get("font_size", 10)))
        app.setFont(f)
        app.setStyleSheet(theme.stylesheet(translator.is_rtl))

    def closeEvent(self, e):
        for p in self.pages.values():
            if hasattr(p, "panel"):
                p.panel.stop()
        self.ctx.db.close()
        super().closeEvent(e)
