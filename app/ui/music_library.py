"""Affichage et import de la bibliotheque musicale."""

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QFrame,
    QHeaderView,
    QLabel,
    QLineEdit,
    QToolButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from app.core.metadata import Track
from app.ui.icon_utils import themed_icon

ICONS_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "icons"


class MusicLibrary(QWidget):
    files_selected = Signal(list)
    track_activated = Signal(str)
    refresh_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        heading = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("Votre musique")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Toute votre collection, au même endroit.")
        subtitle.setObjectName("mutedText")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        heading.addLayout(titles)
        heading.addStretch()

        self.track_count = QLabel("0 MORCEAU")
        self.track_count.setObjectName("countBadge")
        heading.addWidget(self.track_count)

        refresh_button = QToolButton()
        refresh_button.setObjectName("libraryActionButton")
        refresh_button.setAccessibleName("Actualiser les métadonnées")
        refresh_button.setToolTip("Actualiser les métadonnées")
        refresh_button.setIcon(QIcon(str(ICONS_DIRECTORY / "refresh.svg")))
        refresh_button.setIconSize(QSize(19, 19))
        refresh_button.setFixedSize(40, 40)
        self.refresh_button = refresh_button
        refresh_button.clicked.connect(self.refresh_requested.emit)
        heading.addWidget(refresh_button)

        import_button = QToolButton()
        import_button.setObjectName("importButton")
        import_button.setAccessibleName("Importer des musiques")
        import_button.setToolTip("Importer des musiques")
        import_button.setIcon(QIcon(str(ICONS_DIRECTORY / "import.svg")))
        import_button.setIconSize(QSize(19, 19))
        import_button.setFixedSize(40, 40)
        import_button.clicked.connect(self._choose_files)
        heading.addWidget(import_button)
        layout.addLayout(heading)

        self.search = QLineEdit()
        self.search.setObjectName("searchField")
        self.search.setPlaceholderText("Rechercher un titre, un artiste ou un album")
        self.search.textChanged.connect(self._filter_tracks)
        layout.addWidget(self.search)

        table_frame = QFrame()
        table_frame.setObjectName("tableFrame")
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 8, 0, 0)
        self.track_table = QTableWidget(0, 5)
        self.track_table.setObjectName("libraryTable")
        self.track_table.setHorizontalHeaderLabels(
            ["#", "TITRE", "ARTISTE", "ALBUM", "DUREE"]
        )
        self.track_table.verticalHeader().hide()
        self.track_table.setShowGrid(False)
        self.track_table.setAlternatingRowColors(False)
        self.track_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.track_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.track_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.track_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.track_table.setSortingEnabled(False)
        header = self.track_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 52)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 76)
        self.track_table.cellDoubleClicked.connect(self._activate_row)
        table_layout.addWidget(self.track_table)
        self.empty_state = QLabel(
            "Votre bibliothèque est encore vide.\n"
            "Importez vos premiers morceaux pour commencer."
        )
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_layout.addWidget(self.empty_state, 1)
        layout.addWidget(table_frame, 1)
        self._tracks: list[Track] = []
        self.set_theme("dark")

    def set_theme(self, theme: str) -> None:
        self.refresh_button.setIcon(themed_icon("refresh", theme))

    def set_tracks(self, tracks: list[Track]) -> None:
        self._tracks = list(tracks)
        self.track_table.setRowCount(len(self._tracks))
        for row, track in enumerate(self._tracks):
            values = (
                str(row + 1),
                track.title,
                track.artist,
                track.album,
                self._format_duration(track.duration),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, track.path)
                if column == 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 4:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                self.track_table.setItem(row, column, item)
            self.track_table.setRowHeight(row, 58)

        self.track_count.setText(
            f"{len(self._tracks)} MORCEAU"
            + ("" if len(self._tracks) == 1 else "X")
        )
        self._filter_tracks(self.search.text())

    def selected_path(self) -> str | None:
        row = self.track_table.currentRow()
        if row < 0:
            return None
        item = self.track_table.item(row, 1)
        return str(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def set_current_path(self, path: str) -> None:
        for row in range(self.track_table.rowCount()):
            item = self.track_table.item(row, 1)
            if item and item.data(Qt.ItemDataRole.UserRole) == path:
                self.track_table.selectRow(row)
                return

    def _filter_tracks(self, query: str) -> None:
        query = query.strip().casefold()
        visible_count = 0
        for row, track in enumerate(self._tracks):
            searchable = f"{track.title} {track.artist} {track.album}".casefold()
            visible = not query or query in searchable
            self.track_table.setRowHidden(row, not visible)
            visible_count += int(visible)
        if not self._tracks:
            self.empty_state.setText(
                "Votre bibliothèque est encore vide.\n"
                "Importez vos premiers morceaux pour commencer."
            )
        elif query and not visible_count:
            self.empty_state.setText("Aucun morceau ne correspond à votre recherche.")

        self.track_table.setVisible(bool(self._tracks) and bool(visible_count))
        self.empty_state.setVisible(
            not self._tracks or (bool(query) and not visible_count)
        )

    def _choose_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Importer des fichiers audio",
            "",
            "Fichiers audio (*.mp3 *.wav *.ogg)",
        )
        if files:
            self.files_selected.emit(files)

    def _activate_row(self, row: int, _column: int) -> None:
        item = self.track_table.item(row, 1)
        if item:
            self.track_activated.emit(str(item.data(Qt.ItemDataRole.UserRole)))

    @staticmethod
    def _format_duration(duration: float) -> str:
        if duration <= 0:
            return "—"
        minutes, seconds = divmod(int(duration), 60)
        return f"{minutes}:{seconds:02d}"
