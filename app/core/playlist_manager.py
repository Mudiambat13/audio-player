"""Gestion de la file de lecture."""

from app.core.metadata import Track


class PlaylistManager:
    def __init__(self) -> None:
        self._tracks: list[Track] = []
        self._current_index = -1

    @property
    def tracks(self) -> tuple[Track, ...]:
        return tuple(self._tracks)

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def current_track(self) -> Track | None:
        if 0 <= self._current_index < len(self._tracks):
            return self._tracks[self._current_index]
        return None

    def add(self, track: Track) -> bool:
        if any(existing.path == track.path for existing in self._tracks):
            return False
        self._tracks.append(track)
        return True

    def update_track(self, track: Track) -> None:
        for index, existing in enumerate(self._tracks):
            if existing.path == track.path:
                self._tracks[index] = track
                return
        self._tracks.append(track)

    def set_tracks(self, tracks: list[Track]) -> None:
        current_path = self.current_track.path if self.current_track else None
        self._tracks = list(tracks)
        self._current_index = next(
            (index for index, track in enumerate(self._tracks)
             if track.path == current_path),
            -1,
        )

    def select(self, index: int) -> Track | None:
        if not 0 <= index < len(self._tracks):
            return None
        self._current_index = index
        return self.current_track

    def select_path(self, path: str) -> Track | None:
        for index, track in enumerate(self._tracks):
            if track.path == path:
                return self.select(index)
        return None

    def next_track(self) -> Track | None:
        if not self._tracks:
            return None
        self._current_index = (self._current_index + 1) % len(self._tracks)
        return self.current_track

    def previous_track(self) -> Track | None:
        if not self._tracks:
            return None
        if self._current_index < 0:
            self._current_index = 0
        else:
            self._current_index = (self._current_index - 1) % len(self._tracks)
        return self.current_track
