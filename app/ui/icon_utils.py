"""Chargement des icones SVG adaptees au theme courant."""

from pathlib import Path

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

ICONS_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "icons"


def themed_icon(name: str, theme: str) -> QIcon:
    source = (ICONS_DIRECTORY / f"{name}.svg").read_text(encoding="utf-8")
    if theme == "light":
        source = source.replace("#C9CBD5", "#626777")

    renderer = QSvgRenderer(QByteArray(source.encode("utf-8")))
    if not renderer.isValid():
        raise ValueError(f"Icone SVG invalide : {name}")

    pixmap = QPixmap(48, 48)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)
