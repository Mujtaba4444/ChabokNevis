"""ChabokNevis entry point."""

import sys

from PySide6.QtGui import QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from app.core.config import resource_path
from app.core.constants import APP_NAME
from app.services.context import build_context


def main() -> int:
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    # Use native Windows style to preserve window decorations (title bar, snap, etc.)
    # Fusion style does not include native window frames, causing title bar loss after snap
    if sys.platform == "win32":
        app.setStyle("Windows")
    else:
        app.setStyle("Fusion")

    # Set ChabokNevis application icon
    icon_path = resource_path("icons") / "chaboknevis.ico"

    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Load bundled fonts
    for ttf in resource_path("fonts").glob("*.[to]tf"):
        QFontDatabase.addApplicationFont(str(ttf))

    from app.ui.main_window import MainWindow

    window = MainWindow(build_context())
    window.showMaximized()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())