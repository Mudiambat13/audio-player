"""Page de lecture dediee au morceau en cours."""

from PySide6.QtCore import QSignalBlocker, QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.icon_utils import themed_icon
from app.ui.player_controls import PlayerControls


class NowPlayingView(QWidget):
    previous_requested = Signal()
    play_requested = Signal()
    pause_requested = Signal()
    next_requested = Signal()
    seek_requested = Signal(int)
    repeat_mode_changed = Signal(int)
    shuffle_changed = Signal(bool)
    volume_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        heading = QLabel("EN COURS DE LECTURE")
        heading.setObjectName("nowPlayingEyebrow")
        layout.addWidget(heading, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.artwork = QLabel("♫")
        self.artwork.setObjectName("nowPlayingArtwork")
        self.artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork.setFixedSize(300, 300)
        layout.addWidget(self.artwork, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.song_title = QLabel("Aucun morceau sélectionné")
        self.song_title.setObjectName("nowPlayingTitle")
        self.song_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.song_title.setWordWrap(True)
        layout.addWidget(self.song_title)

        self.artist_album = QLabel("Choisissez un titre dans votre bibliothèque")
        self.artist_album.setObjectName("nowPlayingSubtitle")
        self.artist_album.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artist_album.setWordWrap(True)
        layout.addWidget(self.artist_album)

        progress_row = QHBoxLayout()
        progress_row.setContentsMargins(18, 0, 18, 0)
        self.elapsed_label = QLabel("0:00")
        self.elapsed_label.setObjectName("mutedText")
        self.progress = QSlider(Qt.Orientation.Horizontal)
        self.progress.setRange(0, 1)
        self.progress.sliderReleased.connect(
            lambda: self.seek_requested.emit(self.progress.value())
        )
        self.duration_label = QLabel("0:00")
        self.duration_label.setObjectName("mutedText")
        progress_row.addWidget(self.elapsed_label)
        progress_row.addWidget(self.progress, 1)
        progress_row.addWidget(self.duration_label)
        layout.addLayout(progress_row)

        controls = QHBoxLayout()
        controls.setSpacing(14)
        controls.addStretch()

        self.shuffle_button = self._button("shuffle", "Lecture aléatoire")
        self.shuffle_button.setCheckable(True)
        self.shuffle_button.toggled.connect(self.shuffle_changed.emit)
        controls.addWidget(self.shuffle_button)

        self.previous_button = self._button("previous", "Morceau précédent")
        self.previous_button.clicked.connect(self.previous_requested.emit)
        controls.addWidget(self.previous_button)

        self.play_button = self._button("play", "Lire", "nowPlayingPlayButton")
        self.play_button.clicked.connect(self._toggle_playback)
        controls.addWidget(self.play_button)

        self.next_button = self._button("next", "Morceau suivant")
        self.next_button.clicked.connect(self.next_requested.emit)
        controls.addWidget(self.next_button)

        self.repeat_button = self._button("repeat", "Répétition désactivée")
        self.repeat_button.setCheckable(True)
        self.repeat_button.clicked.connect(self._cycle_repeat_mode)
        controls.addWidget(self.repeat_button)
        controls.addStretch()
        layout.addLayout(controls)

        volume_row = QHBoxLayout()
        volume_row.addStretch()
        volume_icon = QLabel("VOLUME")
        volume_icon.setObjectName("mutedText")
        volume_row.addWidget(volume_icon)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(70)
        self.volume.setFixedWidth(150)
        self.volume.valueChanged.connect(self.volume_changed.emit)
        volume_row.addWidget(self.volume)
        volume_row.addStretch()
        layout.addLayout(volume_row)
        self._theme = "dark"

        layout.addStretch(1)
        self._repeat_mode = 0
        self._is_playing = False

    @staticmethod
    def _button(
        icon_name: str,
        accessible_name: str,
        object_name: str = "iconButton",
    ) -> QToolButton:
        button = QToolButton()
        button.setObjectName(object_name)
        button.setAccessibleName(accessible_name)
        button.setToolTip(accessible_name)
        button.setProperty("icon_name", icon_name)
        button.setIcon(themed_icon(icon_name, "dark"))
        button.setIconSize(QSize(22, 22))
        button.setFixedSize(44, 44)
        return button

    def set_track(
        self,
        title: str,
        artist: str,
        album: str,
        duration: float,
        artwork: bytes | None,
    ) -> None:
        self.song_title.setText(title)
        self.artist_album.setText(f"{artist}  ·  {album}")
        pixmap = QPixmap()
        if artwork and pixmap.loadFromData(artwork):
            self.artwork.setPixmap(
                pixmap.scaled(
                    self.artwork.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.artwork.setText("")
        else:
            self.artwork.setPixmap(QPixmap())
            self.artwork.setText("♫")
        self.artwork.setToolTip(f"{album} — {artist}")
        self.progress.setRange(0, max(1, int(duration)))
        self.progress.setValue(0)
        self.elapsed_label.setText("0:00")
        self.duration_label.setText(PlayerControls._format_time(duration))

    def set_position(self, position: float, duration: float) -> None:
        if not self.progress.isSliderDown():
            self.progress.setValue(min(self.progress.maximum(), max(0, int(position))))
        self.elapsed_label.setText(PlayerControls._format_time(position))
        self.duration_label.setText(PlayerControls._format_time(duration))

    def set_playing(self, is_playing: bool) -> None:
        self._is_playing = is_playing
        icon = "pause" if is_playing else "play"
        label = "Mettre en pause" if is_playing else "Lire"
        self._set_button_icon(self.play_button, icon)
        self.play_button.setAccessibleName(label)
        self.play_button.setToolTip(label)

    def set_repeat_mode(self, mode: int) -> None:
        self._repeat_mode = mode
        icon = "repeat-one" if mode == 2 else "repeat"
        labels = ("Répétition désactivée", "Répéter la file", "Répéter le morceau")
        self._set_button_icon(self.repeat_button, icon)
        self.repeat_button.setAccessibleName(labels[mode])
        self.repeat_button.setToolTip(labels[mode])
        blocker = QSignalBlocker(self.repeat_button)
        self.repeat_button.setChecked(mode != 0)
        del blocker

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        for button in self.findChildren(QToolButton):
            icon_name = button.property("icon_name")
            if icon_name:
                button.setIcon(themed_icon(str(icon_name), theme))

    def _set_button_icon(self, button: QToolButton, icon_name: str) -> None:
        button.setProperty("icon_name", icon_name)
        button.setIcon(themed_icon(icon_name, self._theme))

    def set_shuffle(self, enabled: bool) -> None:
        blocker = QSignalBlocker(self.shuffle_button)
        self.shuffle_button.setChecked(enabled)
        del blocker

    def set_volume(self, value: int) -> None:
        blocker = QSignalBlocker(self.volume)
        self.volume.setValue(value)
        del blocker

    def _toggle_playback(self) -> None:
        if self._is_playing:
            self.pause_requested.emit()
        else:
            self.play_requested.emit()

    def _cycle_repeat_mode(self) -> None:
        self.set_repeat_mode((self._repeat_mode + 1) % 3)
        self.repeat_mode_changed.emit(self._repeat_mode)
