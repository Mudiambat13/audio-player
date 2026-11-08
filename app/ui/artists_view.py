"""Vue des artistes de la bibliotheque."""

from collections import defaultdict
from dataclasses import dataclass, field

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.core.metadata import Track


@dataclass
class _Artist:
    name: str
    albums: set[str] = field(default_factory=set)
    track_count: int = 0
    artwork: bytes | None = None


class ArtistsView(QWidget):
    artist_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Artistes")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Retrouvez tous les artistes de votre collection.")
        subtitle.setObjectName("mutedText")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setObjectName("artistsScrollArea")
        self.content = QWidget()
        self.content.setObjectName("artistsContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 8, 8, 8)
        self.content_layout.setSpacing(16)
        self.scroll_area.setWidget(self.content)
        layout.addWidget(self.scroll_area, 1)

    def set_tracks(self, tracks: list[Track]) -> None:
        self._clear_layout(self.content_layout)

        artists: dict[str, _Artist] = {}
        for track in tracks:
            name = track.artist.strip() or "Artiste inconnu"
            key = name.casefold()
            artist = artists.setdefault(key, _Artist(name))
            artist.track_count += 1
            album = track.album.strip() or "Album inconnu"
            artist.albums.add(album.casefold())
            if artist.artwork is None and track.artwork:
                artist.artwork = track.artwork

        if not artists:
            empty = QLabel("Aucun artiste pour le moment.\nImportez des morceaux pour les découvrir ici.")
            empty.setObjectName("emptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        sorted_artists = sorted(
            artists.values(),
            key=lambda artist: artist.name.casefold(),
        )
        for index, artist in enumerate(sorted_artists):
            card = self._artist_card(
                artist.name,
                artist.track_count,
                len(artist.albums),
                artist.artwork,
            )
            grid.addWidget(card, index // 4, index % 4)
        grid.setColumnStretch(4, 1)
        self.content_layout.addLayout(grid)
        self.content_layout.addStretch()

    @classmethod
    def _clear_layout(cls, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            widget = item.widget()
            if child_layout is not None:
                cls._clear_layout(child_layout)
                child_layout.deleteLater()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _artist_card(
        self,
        artist: str,
        track_count: int,
        album_count: int,
        artwork: bytes | None,
    ) -> QToolButton:
        card = QToolButton()
        card.setObjectName("artistCard")
        card.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        card.setText(
            f"{artist}\n{track_count} morceau"
            + ("" if track_count == 1 else "x")
            + f" · {album_count} album"
            + ("" if album_count == 1 else "s")
        )
        pixmap = self._artist_pixmap(artwork, artist)
        card.setIcon(QIcon(pixmap))
        card.setIconSize(pixmap.size())
        card.setFixedSize(184, 218)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setToolTip(f"{artist}\nAfficher les morceaux de cet artiste")
        card.clicked.connect(
            lambda checked=False, selected_artist=artist:
            self.artist_requested.emit(selected_artist)
        )
        return card

    @staticmethod
    def _artist_pixmap(artwork: bytes | None, artist: str) -> QPixmap:
        size = 136
        pixmap = QPixmap()
        if artwork and pixmap.loadFromData(artwork):
            return pixmap.scaled(
                size,
                size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

        pixmap = QPixmap(size, size)
        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0, QColor("#46386B"))
        gradient.setColorAt(1, QColor("#1C2739"))
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, size, size, 68, 68)
        painter.setPen(QColor("#E2D9FF"))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            artist[:1].upper() or "♫",
        )
        painter.end()
        return pixmap
