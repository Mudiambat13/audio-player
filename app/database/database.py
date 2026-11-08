"""Persistance de la bibliotheque musicale avec SQLite."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.metadata import Track


def _default_database_path() -> Path:
    if os.name == "nt":
        data_dir = Path(os.environ.get("APPDATA", Path.home())) / "JonathanMusicPlayer"
    else:
        data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        data_dir /= "jonathan-music-player"
    return data_dir / "library.db"


class LibraryDatabase:
    def __init__(self, database_path: str | Path | None = None) -> None:
        self.path = Path(database_path) if database_path else _default_database_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tracks (
                    path TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT NOT NULL,
                    duration REAL NOT NULL DEFAULT 0,
                    artwork BLOB,
                    artwork_mime TEXT
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(tracks)").fetchall()
            }
            if "artwork" not in columns:
                connection.execute("ALTER TABLE tracks ADD COLUMN artwork BLOB")
            if "artwork_mime" not in columns:
                connection.execute("ALTER TABLE tracks ADD COLUMN artwork_mime TEXT")

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def add_track(self, track: Track) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO tracks (
                    path, title, artist, album, duration, artwork, artwork_mime
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    track.path,
                    track.title,
                    track.artist,
                    track.album,
                    track.duration,
                    track.artwork,
                    track.artwork_mime,
                ),
            )
        return cursor.rowcount > 0

    def save_track(self, track: Track) -> None:
        """Insere ou actualise les tags relus depuis le fichier audio."""
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tracks (
                    path, title, artist, album, duration, artwork, artwork_mime
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    title = excluded.title,
                    artist = excluded.artist,
                    album = excluded.album,
                    duration = excluded.duration,
                    artwork = COALESCE(excluded.artwork, tracks.artwork),
                    artwork_mime = COALESCE(excluded.artwork_mime, tracks.artwork_mime)
                """,
                (
                    track.path,
                    track.title,
                    track.artist,
                    track.album,
                    track.duration,
                    track.artwork,
                    track.artwork_mime,
                ),
            )

    def get_tracks(self) -> list[Track]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT path, title, artist, album, duration, artwork, artwork_mime
                FROM tracks
                ORDER BY title COLLATE NOCASE, artist COLLATE NOCASE
                """
            ).fetchall()
        return [
            Track(
                path=row["path"],
                title=row["title"],
                artist=row["artist"],
                album=row["album"],
                duration=row["duration"],
                artwork=row["artwork"],
                artwork_mime=row["artwork_mime"],
            )
            for row in rows
        ]

    def remove_track(self, path: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM tracks WHERE path = ?", (path,))
        return cursor.rowcount > 0
