"""Commandes de lecture audio."""

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


class PlayerControls(QWidget):
    previous_requested = Signal()
    play_requested = Signal()
    pause_requested = Signal()
    next_requested = Signal()
    seek_requested = Signal(int)
    volume_changed = Signal(int)
    repeat_mode_changed = Signal(int)
    shuffle_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("player")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(22)

        self.artwork = QLabel("♫")
        self.artwork.setObjectName("albumArtwork")
        self.artwork.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.artwork.setFixedSize(58, 58)
        layout.addWidget(self.artwork)

        metadata = QVBoxLayout()
        metadata.setSpacing(5)
        self.song_title = QLabel("Aucun morceau sélectionné")
        self.song_title.setObjectName("songTitle")
        self.song_title.setMinimumWidth(140)
        self.song_title.setMaximumWidth(240)
        self.song_title.setWordWrap(True)
        self.song_artist = QLabel("Choisissez un titre")
        self.song_artist.setObjectName("mutedText")
        self.song_artist.setMinimumWidth(140)
        self.song_artist.setMaximumWidth(240)
        self.song_artist.setWordWrap(True)
        metadata.addWidget(self.song_title)
        metadata.addWidget(self.song_artist)
        layout.addLayout(metadata, 2)

        player = QVBoxLayout()
        player.setSpacing(6)
        controls = QHBoxLayout()
        controls.setSpacing(12)
        controls.addStretch()

        self.shuffle_button = self._icon_button("shuffle", "Lecture aléatoire")
        self.shuffle_button.setCheckable(True)
        self.shuffle_button.toggled.connect(self.shuffle_changed.emit)
        controls.addWidget(self.shuffle_button)

        self.repeat_button = self._icon_button("repeat", "Répétition désactivée")
        self.repeat_button.setCheckable(True)
        self.repeat_button.clicked.connect(self._cycle_repeat_mode)
        controls.addWidget(self.repeat_button)

        self.previous_button = self._icon_button("previous", "Morceau précédent")
        self.previous_button.clicked.connect(self.previous_requested.emit)
        controls.addWidget(self.previous_button)

        self.play_button = self._icon_button("play", "Lire", "playButton")
        self.play_button.clicked.connect(self._toggle_playback)
        controls.addWidget(self.play_button)

        self.next_button = self._icon_button("next", "Morceau suivant")
        self.next_button.clicked.connect(self.next_requested.emit)
        controls.addWidget(self.next_button)

        controls.addStretch()
        player.addLayout(controls)

        progress_row = QHBoxLayout()
        self.elapsed_label = QLabel("0:00")
        self.progress = QSlider(Qt.Orientation.Horizontal)
        self.progress.setRange(0, 1)
        self.progress.sliderReleased.connect(
            lambda: self.seek_requested.emit(self.progress.value())
        )
        self.duration_label = QLabel("0:00")
        progress_row.addWidget(self.elapsed_label)
        progress_row.addWidget(self.progress, 1)
        progress_row.addWidget(self.duration_label)
        player.addLayout(progress_row)
        layout.addLayout(player, 4)

        volume = QVBoxLayout()
        volume.addWidget(QLabel("VOLUME"))
        volume_controls = QHBoxLayout()
        self.volume_button = self._icon_button("volume", "Couper le son")
        self.volume_button.setCheckable(True)
        self.volume_button.toggled.connect(self._toggle_mute)
        volume_controls.addWidget(self.volume_button)
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(70)
        self.volume.setFixedWidth(90)
        self.volume.valueChanged.connect(self.volume_changed.emit)
        self.volume.valueChanged.connect(self._update_volume_icon)
        volume_controls.addWidget(self.volume)
        volume.addLayout(volume_controls)
        layout.addLayout(volume)
        self._repeat_mode = 0
        self._is_playing = False
        self._last_volume = 70
        self._theme = "dark"

    @staticmethod
    def _icon_button(
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
        button.setIconSize(QSize(20, 20))
        button.setFixedSize(38, 38)
        return button

    def _toggle_playback(self) -> None:
        if self._is_playing:
            self.pause_requested.emit()
        else:
            self.play_requested.emit()

    def set_playing(self, is_playing: bool) -> None:
        self._is_playing = is_playing
        icon_name = "pause" if is_playing else "play"
        accessible_name = "Mettre en pause" if is_playing else "Lire"
        self._set_button_icon(self.play_button, icon_name)
        self.play_button.setAccessibleName(accessible_name)
        self.play_button.setToolTip(accessible_name)

    def set_repeat_mode(self, mode: int) -> None:
        self._repeat_mode = mode
        icon_name = "repeat-one" if mode == 2 else "repeat"
        labels = ("Répétition désactivée", "Répéter la file", "Répéter le morceau")
        self._set_button_icon(self.repeat_button, icon_name)
        self.repeat_button.setAccessibleName(labels[mode])
        self.repeat_button.setToolTip(labels[mode])
        blocker = QSignalBlocker(self.repeat_button)
        self.repeat_button.setChecked(mode != 0)
        del blocker

    def set_shuffle(self, enabled: bool) -> None:
        blocker = QSignalBlocker(self.shuffle_button)
        self.shuffle_button.setChecked(enabled)
        del blocker

    def set_volume(self, value: int) -> None:
        blocker = QSignalBlocker(self.volume)
        self.volume.setValue(value)
        del blocker

    def _cycle_repeat_mode(self) -> None:
        self.set_repeat_mode((self._repeat_mode + 1) % 3)
        self.repeat_mode_changed.emit(self._repeat_mode)

    def _toggle_mute(self, muted: bool) -> None:
        if muted:
            if self.volume.value() > 0:
                self._last_volume = self.volume.value()
            self.volume.setValue(0)
        else:
            self.volume.setValue(self._last_volume or 70)
        self._update_volume_icon(self.volume.value())

    def _update_volume_icon(self, value: int) -> None:
        muted = value == 0
        self._set_button_icon(self.volume_button, "mute" if muted else "volume")
        self.volume_button.setToolTip("Activer le son" if muted else "Couper le son")
        if not muted:
            self._last_volume = value
        if self.volume_button.isChecked() != muted:
            blocker = QSignalBlocker(self.volume_button)
            self.volume_button.setChecked(muted)
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

    def set_track(
        self,
        title: str,
        artist: str,
        album: str,
        duration: float,
        artwork: bytes | None = None,
    ) -> None:
        self.song_title.setText(title)
        self.song_artist.setText(f"{artist}  ·  {album}")
        self.set_artwork(artwork)
        self.progress.setRange(0, max(1, int(duration)))
        self.progress.setValue(0)
        self.elapsed_label.setText("0:00")
        self.duration_label.setText(self._format_time(duration))

    def set_artwork(self, artwork: bytes | None) -> None:
        pixmap = QPixmap()
        if artwork and pixmap.loadFromData(artwork):
            size = self.artwork.size()
            scaled = pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = (scaled.width() - size.width()) // 2
            y = (scaled.height() - size.height()) // 2
            self.artwork.setPixmap(scaled.copy(x, y, size.width(), size.height()))
            self.artwork.setText("")
        else:
            self.artwork.setPixmap(QPixmap())
            self.artwork.setText("♫")

    def set_position(self, position: float, duration: float) -> None:
        if not self.progress.isSliderDown():
            self.progress.setValue(
                min(self.progress.maximum(), max(0, int(position)))
            )
        self.elapsed_label.setText(self._format_time(position))
        self.duration_label.setText(self._format_time(duration))

    @staticmethod
    def _format_time(seconds: float) -> str:
        total_seconds = max(0, int(seconds))
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"
