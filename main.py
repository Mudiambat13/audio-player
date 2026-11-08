"""Point d'entree de Jonathan Music Player."""

import sys
import sqlite3
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.ui.main_window import MainWindow

ICONS_DIRECTORY = Path(__file__).resolve().parent / "assets" / "icons"


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Jonathan")
    app.setOrganizationName("Jonathan")
    app.setWindowIcon(QIcon(str(ICONS_DIRECTORY / "app.svg")))

    try:
        window = MainWindow()
    except (ImportError, OSError, RuntimeError, sqlite3.Error) as error:
        QMessageBox.critical(
            None,
            "Impossible de démarrer",
            f"Le lecteur n'a pas pu démarrer : {error}",
        )
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
