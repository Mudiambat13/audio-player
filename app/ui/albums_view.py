"""Vue des albums regroupes par artiste."""

from collections import defaultdict

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.core.metadata import Track


class AlbumsView(QWidget):
    filter_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        title = QLabel("Albums")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Parcourez les albums regroupés par artiste.")
        subtitle.setObjectName("mutedText")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setObjectName("albumsScrollArea")
        self.content = QWidget()
        self.content.setObjectName("albumsContent")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 8, 8, 8)
        self.content_layout.setSpacing(24)
        self.scroll_area.setWidget(self.content)
        layout.addWidget(self.scroll_area, 1)

    def set_tracks(self, tracks: list[Track]) -> None:
        self._clear_layout(self.content_layout)

        artists: dict[str, dict[str, list[Track]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for track in tracks:
            artist = track.artist.strip() or "Artiste inconnu"
            album = track.album.strip() or "Album inconnu"
            artists[artist][album].append(track)

        if not artists:
            empty = QLabel("Aucun album pour le moment.\nImportez des morceaux pour les découvrir ici.")
            empty.setObjectName("emptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(empty)
            self.content_layout.addStretch()
            return

        for artist in sorted(artists, key=str.casefold):
            albums = artists[artist]
            header = QHBoxLayout()
            artist_label = QLabel(artist)
            artist_label.setObjectName("artistHeading")
            album_count = QLabel(
                f"{len(albums)} ALBUM" + ("" if len(albums) == 1 else "S")
            )
            album_count.setObjectName("countBadge")
            header.addWidget(artist_label)
            header.addWidget(album_count)
            header.addStretch()
            self.content_layout.addLayout(header)

            grid = QGridLayout()
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(14)
            grid.setVerticalSpacing(14)
            for index, album in enumerate(sorted(albums, key=str.casefold)):
                album_tracks = albums[album]
                cover = next(
                    (track.artwork for track in album_tracks if track.artwork),
                    None,
                )
                card = self._album_card(
                    artist,
                    album,
                    len(album_tracks),
                    cover,
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

    def _album_card(
        self,
        artist: str,
        album: str,
        track_count: int,
        cover: bytes | None,
    ) -> QToolButton:
        card = QToolButton()
        card.setObjectName("albumCard")
        card.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        card.setText(f"{album}\n{track_count} titre" + ("" if track_count == 1 else "s"))
        cover_pixmap = self._cover_pixmap(cover, album)
        card.setIcon(QIcon(cover_pixmap))
        card.setIconSize(cover_pixmap.size())
        card.setFixedSize(184, 226)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setToolTip(f"{album} — {artist}\nCliquez pour afficher les morceaux")
        card.clicked.connect(
            lambda checked=False, selected_artist=artist, selected_album=album:
            self.filter_requested.emit(f"{selected_artist} {selected_album}")
        )
        return card

    @staticmethod
    def _cover_pixmap(cover: bytes | None, album: str) -> QPixmap:
        size = 148
        pixmap = QPixmap()
        if cover and pixmap.loadFromData(cover):
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
        painter.drawRoundedRect(0, 0, size, size, 12, 12)
        painter.setPen(QColor("#E2D9FF"))
        font = QFont("Segoe UI", 46, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "♫")
        painter.end()
        return pixmap
