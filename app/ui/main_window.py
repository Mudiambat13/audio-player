"""Fenetre principale de Jonathan Music Player."""

import sqlite3
import random
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)

from app.core.audio_engine import AudioEngine, AudioEngineError
from app.core.metadata import Track, read_metadata
from app.core.playlist_manager import PlaylistManager
from app.database.database import LibraryDatabase
from app.ui.albums_view import AlbumsView
from app.ui.artists_view import ArtistsView
from app.ui.music_library import MusicLibrary
from app.ui.now_playing_view import NowPlayingView
from app.ui.player_controls import PlayerControls
from app.ui.sidebar import Sidebar
from app.ui.styles import stylesheet_for_theme

ICONS_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "icons"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Jonathan")
        self.setWindowIcon(QIcon(str(ICONS_DIRECTORY / "app.svg")))
        self.setMinimumSize(1050, 650)
        self.settings = QSettings("Jonathan", "Jonathan")
        saved_theme = self.settings.value("theme", "dark", type=str)
        self._theme = saved_theme if saved_theme in ("dark", "light") else "dark"

        self.database = LibraryDatabase()
        self.audio = AudioEngine()
        self.playlist = PlaylistManager()
        self.playlist.set_tracks(self.database.get_tracks())
        self._playing = False
        self._paused = False
        self._repeat_mode = 0
        self._shuffle_enabled = False
        self._shuffle_history: list[str] = []

        self._setup_ui()
        self._refresh_tracks()
        self.audio.set_volume(0.7)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(250)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.page_requested.connect(self._show_page)
        self.sidebar.theme_toggle_requested.connect(self._toggle_theme)
        self.sidebar.set_theme(self._theme)
        main_layout.addWidget(self.sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(34, 28, 34, 20)
        content_layout.setSpacing(18)

        self.pages = QStackedWidget()
        self._page_indexes: dict[str, int] = {}
        self.pages.addWidget(self._create_home_page())
        self._page_indexes["home"] = 0

        self.library = MusicLibrary()
        self.library.files_selected.connect(self._import_files)
        self.library.track_activated.connect(self._play_path)
        self.library.refresh_requested.connect(self._refresh_metadata)
        self.pages.addWidget(self.library)
        self._page_indexes["library"] = 1

        self.albums_view = AlbumsView()
        self.albums_view.filter_requested.connect(self._open_album)
        self.pages.addWidget(self.albums_view)
        self._page_indexes["albums"] = 2

        self.artists_view = ArtistsView()
        self.artists_view.artist_requested.connect(self._open_artist)
        self.pages.addWidget(self.artists_view)
        self._page_indexes["artists"] = 3

        self.now_playing_view = NowPlayingView()
        self.now_playing_view.previous_requested.connect(self._play_previous)
        self.now_playing_view.play_requested.connect(self._play_or_resume)
        self.now_playing_view.pause_requested.connect(self._pause)
        self.now_playing_view.next_requested.connect(self._play_next)
        self.now_playing_view.seek_requested.connect(self._seek)
        self.now_playing_view.repeat_mode_changed.connect(self._set_repeat_mode)
        self.now_playing_view.shuffle_changed.connect(self._set_shuffle)
        self.now_playing_view.volume_changed.connect(self._set_volume)
        self.pages.addWidget(self.now_playing_view)
        self._page_indexes["now_playing"] = 4

        queue_page = QWidget()
        queue_layout = QVBoxLayout(queue_page)
        queue_title = QLabel("File de lecture")
        queue_title.setObjectName("pageTitle")
        queue_subtitle = QLabel("Les morceaux de votre bibliothèque, prêts à être écoutés.")
        queue_subtitle.setObjectName("mutedText")
        self.queue_list = QListWidget()
        self.queue_list.itemDoubleClicked.connect(self._play_queue_item)
        queue_layout.addWidget(queue_title)
        queue_layout.addWidget(queue_subtitle)
        queue_layout.addWidget(self.queue_list)
        self.pages.addWidget(queue_page)
        self._page_indexes["queue"] = 5
        self.pages.setCurrentIndex(self._page_indexes["library"])
        content_layout.addWidget(self.pages, 1)

        self.player_controls = PlayerControls()
        self.player_controls.previous_requested.connect(self._play_previous)
        self.player_controls.play_requested.connect(self._play_or_resume)
        self.player_controls.pause_requested.connect(self._pause)
        self.player_controls.next_requested.connect(self._play_next)
        self.player_controls.seek_requested.connect(self._seek)
        self.player_controls.volume_changed.connect(
            self._set_volume
        )
        self.player_controls.repeat_mode_changed.connect(self._set_repeat_mode)
        self.player_controls.shuffle_changed.connect(self._set_shuffle)
        self.now_playing_view.set_repeat_mode(self._repeat_mode)
        self.now_playing_view.set_shuffle(self._shuffle_enabled)
        content_layout.addWidget(self.player_controls)
        main_layout.addWidget(content, 1)

        self._apply_theme()

    def _toggle_theme(self) -> None:
        self._theme = "light" if self._theme == "dark" else "dark"
        self.settings.setValue("theme", self._theme)
        self.settings.sync()
        self._apply_theme()

    def _apply_theme(self) -> None:
        self.setStyleSheet(stylesheet_for_theme(self._theme))
        self.sidebar.set_theme(self._theme)
        self.library.set_theme(self._theme)
        self.player_controls.set_theme(self._theme)
        self.now_playing_view.set_theme(self._theme)

    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Bienvenue chez Jonathan")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.library_summary = QLabel()
        self.library_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_library = QPushButton("Ouvrir ma bibliothèque")
        open_library.clicked.connect(lambda: self._show_page("library"))

        layout.addWidget(title)
        layout.addWidget(self.library_summary)
        layout.addSpacing(12)
        layout.addWidget(open_library)
        return page

    def _show_page(self, page: str) -> None:
        index = self._page_indexes.get(page)
        if index is not None:
            self.pages.setCurrentIndex(index)
            self.sidebar.set_active_page(page)

    def _refresh_tracks(self) -> None:
        tracks = self.playlist.tracks
        self.library.set_tracks(list(tracks))
        self.albums_view.set_tracks(list(tracks))
        self.artists_view.set_tracks(list(tracks))
        self.queue_list.clear()
        for track in tracks:
            album = track.album if track.album else "Album inconnu"
            item = QListWidgetItem(
                f"{track.title}\n{track.artist}  ·  {album}"
            )
            item.setData(Qt.ItemDataRole.UserRole, track.path)
            item.setToolTip(track.path)
            self.queue_list.addItem(item)
        count = len(tracks)
        self.library_summary.setText(
            f"{count} morceau{'x' if count > 1 else ''} dans votre collection"
        )
        current_track = self.playlist.current_track
        if current_track is not None:
            self._select_current_queue_item(current_track.path)

    def _open_album(self, query: str) -> None:
        self.library.search.setText(query)
        self._show_page("library")

    def _open_artist(self, artist: str) -> None:
        self.library.search.setText(artist)
        self._show_page("library")

    def _import_files(self, paths: list[str]) -> None:
        added = 0
        missing: list[str] = []
        try:
            known_paths = {track.path for track in self.playlist.tracks}
            for path in paths:
                if not Path(path).is_file():
                    missing.append(path)
                    continue
                track = read_metadata(path)
                self.database.save_track(track)
                self.playlist.update_track(track)
                if track.path not in known_paths:
                    added += 1
                    known_paths.add(track.path)
        except (OSError, sqlite3.Error) as error:
            QMessageBox.critical(
                self,
                "Import impossible",
                f"Un morceau n'a pas pu être ajouté : {error}",
            )
            self._refresh_tracks()
            return

        self.playlist.set_tracks(self.database.get_tracks())
        self._refresh_tracks()
        if missing:
            QMessageBox.warning(
                self,
                "Fichiers introuvables",
                "Certains fichiers n'existent plus :\n" + "\n".join(missing),
            )
        if added:
            QMessageBox.information(
                self,
                "Import terminé",
                f"{added} morceau(x) ajouté(s) à la bibliothèque.",
            )

    def _refresh_metadata(self) -> None:
        updated = 0
        missing: list[str] = []
        try:
            for existing in self.playlist.tracks:
                if not Path(existing.path).is_file():
                    missing.append(existing.path)
                    continue
                track = read_metadata(existing.path)
                self.database.save_track(track)
                self.playlist.update_track(track)
                updated += 1
            self.playlist.set_tracks(self.database.get_tracks())
        except (OSError, sqlite3.Error) as error:
            QMessageBox.critical(
                self,
                "Actualisation impossible",
                f"Les métadonnées n'ont pas pu être actualisées : {error}",
            )
            self._refresh_tracks()
            return

        self._refresh_tracks()
        if missing:
            QMessageBox.warning(
                self,
                "Fichiers introuvables",
                f"{len(missing)} fichier(s) de la bibliothèque sont introuvables.",
            )
        elif updated:
            QMessageBox.information(
                self,
                "Bibliothèque actualisée",
                f"Les métadonnées de {updated} morceau(x) ont été relues.",
            )

    def _play_path(self, path: str) -> None:
        track = self.playlist.select_path(path)
        if track is not None:
            self._start_track(track)

    def _play_queue_item(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self._play_path(str(path))

    def _start_track(self, track: Track) -> None:
        try:
            self.audio.play(track.path)
        except AudioEngineError as error:
            self._playing = False
            self._paused = False
            self.player_controls.set_playing(False)
            self.now_playing_view.set_playing(False)
            QMessageBox.warning(self, "Lecture impossible", str(error))
            return

        self._playing = True
        self._paused = False
        self.player_controls.set_playing(True)
        self.now_playing_view.set_playing(True)
        self.player_controls.set_track(
            track.title,
            track.artist,
            track.album,
            track.duration,
            track.artwork,
        )
        self.now_playing_view.set_track(
            track.title,
            track.artist,
            track.album,
            track.duration,
            track.artwork,
        )
        self._select_current_queue_item(track.path)

    def _play_or_resume(self) -> None:
        selected_path = self._selected_path_for_current_page()
        current_track = self.playlist.current_track

        if self._paused and (
            selected_path is None
            or (current_track is not None and selected_path == current_track.path)
        ):
            try:
                self.audio.resume()
            except AudioEngineError as error:
                QMessageBox.warning(self, "Reprise impossible", str(error))
                return
            self._paused = False
            self._playing = True
            self.player_controls.set_playing(True)
            self.now_playing_view.set_playing(True)
            return

        track = (
            self.playlist.select_path(selected_path)
            if selected_path
            else current_track or self.playlist.select(0)
        )
        if track is not None and (
            not self._playing
            or self._paused
            or current_track is None
            or track.path != current_track.path
        ):
            self._start_track(track)

    def _selected_path_for_current_page(self) -> str | None:
        current_page = self.pages.currentIndex()
        if current_page == self._page_indexes["library"]:
            return self.library.selected_path()
        if current_page == self._page_indexes["queue"]:
            item = self.queue_list.currentItem()
            return (
                str(item.data(Qt.ItemDataRole.UserRole))
                if item is not None
                else None
            )
        return None

    def _pause(self) -> None:
        if self._playing and not self._paused:
            try:
                self.audio.pause()
            except AudioEngineError as error:
                QMessageBox.warning(self, "Pause impossible", str(error))
                return
            self._paused = True
            self.player_controls.set_playing(False)
            self.now_playing_view.set_playing(False)

    def _set_volume(self, value: int) -> None:
        try:
            self.audio.set_volume(value / 100)
        except AudioEngineError as error:
            QMessageBox.warning(self, "Volume impossible", str(error))
        self.player_controls.set_volume(value)
        self.now_playing_view.set_volume(value)

    def _play_next(self) -> None:
        current = self.playlist.current_track
        if self._shuffle_enabled and len(self.playlist.tracks) > 1:
            track = self._random_track()
        else:
            track = self.playlist.next_track()
        if current is not None and track is not None and current.path != track.path:
            self._shuffle_history.append(current.path)
        if track is not None:
            self._start_track(track)

    def _play_previous(self) -> None:
        if self._shuffle_enabled and self._shuffle_history:
            previous_path = self._shuffle_history.pop()
            track = self.playlist.select_path(previous_path)
            if track is not None:
                self._start_track(track)
            return
        track = self.playlist.previous_track()
        if track is not None:
            self._start_track(track)

    def _random_track(self) -> Track | None:
        tracks = self.playlist.tracks
        if not tracks:
            return None
        candidates = [
            index
            for index in range(len(tracks))
            if index != self.playlist.current_index
        ]
        if not candidates:
            return self.playlist.current_track
        return self.playlist.select(random.choice(candidates))

    def _set_repeat_mode(self, mode: int) -> None:
        self._repeat_mode = mode
        self.player_controls.set_repeat_mode(mode)
        self.now_playing_view.set_repeat_mode(mode)

    def _set_shuffle(self, enabled: bool) -> None:
        self._shuffle_enabled = enabled
        self._shuffle_history.clear()
        self.player_controls.set_shuffle(enabled)
        self.now_playing_view.set_shuffle(enabled)

    def _seek(self, position: int) -> None:
        try:
            self.audio.seek(position)
        except AudioEngineError as error:
            QMessageBox.warning(self, "Deplacement impossible", str(error))
        self._update_progress()

    def _select_current_queue_item(self, path: str) -> None:
        for row in range(self.queue_list.count()):
            item = self.queue_list.item(row)
            if item.data(Qt.ItemDataRole.UserRole) == path:
                self.queue_list.setCurrentRow(row)
                self.library.set_current_path(path)
                break

    def _update_progress(self) -> None:
        track = self.playlist.current_track
        if track is None or not self._playing:
            return

        position = self.audio.position
        if track.duration > 0:
            position = min(position, track.duration)
        self.player_controls.set_position(position, track.duration)
        self.now_playing_view.set_position(position, track.duration)
        if not self._paused and not self.audio.is_busy:
            self._advance_after_track()

    def _advance_after_track(self) -> None:
        current = self.playlist.current_track
        if current is None:
            self._playing = False
            self.player_controls.set_playing(False)
            self.now_playing_view.set_playing(False)
            return

        if self._repeat_mode == 2:
            self._start_track(current)
            return

        if self._shuffle_enabled:
            if len(self.playlist.tracks) > 1 or self._repeat_mode == 1:
                next_track = self._random_track()
                if next_track is not None:
                    if next_track.path != current.path:
                        self._shuffle_history.append(current.path)
                    self._start_track(next_track)
                    return

        if self.playlist.current_index + 1 < len(self.playlist.tracks):
            next_track = self.playlist.next_track()
            if next_track is not None:
                self._start_track(next_track)
                return

        if self._repeat_mode == 1:
            first_track = self.playlist.select(0)
            if first_track is not None:
                self._start_track(first_track)
                return

        self._playing = False
        self._paused = False
        self.player_controls.set_playing(False)
        self.now_playing_view.set_playing(False)
        if current.duration > 0:
            self.player_controls.set_position(current.duration, current.duration)

    def closeEvent(self, event) -> None:
        self.timer.stop()
        try:
            self.audio.close()
        except AudioEngineError as error:
            QMessageBox.warning(self, "Fermeture audio", str(error))
        event.accept()
