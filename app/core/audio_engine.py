"""Moteur de lecture audio base sur pygame.mixer."""

import time
from pathlib import Path


class AudioEngineError(RuntimeError):
    """Erreur explicite d'initialisation ou de lecture audio."""


class AudioEngine:
    def __init__(self) -> None:
        try:
            import pygame
        except ImportError as error:
            raise AudioEngineError(f"pygame n'est pas installe : {error}") from error

        try:
            pygame.mixer.init()
        except (pygame.error, OSError, RuntimeError) as error:
            raise AudioEngineError(f"Initialisation audio impossible : {error}") from error

        self._pygame = pygame
        self._position = 0.0
        self._started_at: float | None = None
        self._paused = False
        self._loaded = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    @property
    def is_busy(self) -> bool:
        return self._loaded and not self._paused and self._pygame.mixer.music.get_busy()

    @property
    def position(self) -> float:
        if self._started_at is None or self._paused:
            return self._position
        return self._position + time.monotonic() - self._started_at

    def play(self, file_path: str | Path) -> None:
        try:
            self._pygame.mixer.music.load(str(file_path))
            self._pygame.mixer.music.play()
        except (self._pygame.error, OSError) as error:
            self._loaded = False
            self._started_at = None
            raise AudioEngineError(f"Lecture impossible : {error}") from error

        self._position = 0.0
        self._started_at = time.monotonic()
        self._paused = False
        self._loaded = True

    def pause(self) -> None:
        if not self._loaded or self._paused:
            return
        self._position = self.position
        try:
            self._pygame.mixer.music.pause()
        except self._pygame.error as error:
            raise AudioEngineError(f"Mise en pause impossible : {error}") from error
        self._started_at = None
        self._paused = True

    def resume(self) -> None:
        if not self._loaded or not self._paused:
            return
        try:
            self._pygame.mixer.music.unpause()
        except self._pygame.error as error:
            raise AudioEngineError(f'Reprise impossible : {error}') from error
        self._started_at = time.monotonic()
        self._paused = False

    def stop(self) -> None:
        try:
            self._pygame.mixer.music.stop()
        except self._pygame.error as error:
            raise AudioEngineError(f"Arret audio impossible : {error}") from error
        self._position = 0.0
        self._started_at = None
        self._paused = False
        self._loaded = False

    def seek(self, position: float) -> None:
        if not self._loaded:
            return
        try:
            self._pygame.mixer.music.set_pos(max(0.0, float(position)))
        except self._pygame.error as error:
            raise AudioEngineError(f"Deplacement dans le morceau impossible : {error}") from error

        self._position = max(0.0, float(position))
        if not self._paused:
            self._started_at = time.monotonic()

    def set_volume(self, volume: float) -> None:
        try:
            self._pygame.mixer.music.set_volume(min(1.0, max(0.0, volume)))
        except self._pygame.error as error:
            raise AudioEngineError(f"Reglage du volume impossible : {error}") from error

    def close(self) -> None:
        try:
            self.stop()
            self._pygame.mixer.quit()
        except self._pygame.error as error:
            raise AudioEngineError(f"Fermeture du moteur audio impossible : {error}") from error
