"""Lecture et normalisation des metadonnees musicales."""

from dataclasses import dataclass
import base64
from pathlib import Path
from typing import Any

from mutagen import File as MutagenFile
from mutagen import MutagenError


@dataclass(frozen=True)
class Track:
    path: str
    title: str
    artist: str
    album: str
    duration: float
    artwork: bytes | None = None
    artwork_mime: str | None = None


_TAG_NAMES = {
    "title": ("title", "TIT2", "\xa9nam"),
    "artist": ("artist", "performer", "TPE1", "\xa9ART"),
    "album": ("album", "TALB", "\xa9alb"),
}


def _plain_text(value: Any) -> str:
    if hasattr(value, "text"):
        value = value.text
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    return str(value).strip()


def _tag_value(tags: Any, name: str, fallback: str) -> str:
    if not tags:
        return fallback

    for candidate in _TAG_NAMES[name]:
        value = tags.get(candidate)
        if value is not None:
            text = _plain_text(value)
            if text:
                return text

    normalized_names = {candidate.casefold() for candidate in _TAG_NAMES[name]}
    for key, value in tags.items():
        if str(key).casefold() in normalized_names:
            text = _plain_text(value)
            if text:
                return text

    return fallback


def _image_mime(data: bytes, preferred: str | None = None) -> str:
    if preferred:
        return preferred
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


def _extract_artwork(audio: Any) -> tuple[bytes | None, str | None]:
    if audio is None:
        return None, None

    pictures = getattr(audio, "pictures", None)
    if pictures:
        picture = pictures[0]
        data = getattr(picture, "data", None)
        if data:
            return bytes(data), _image_mime(bytes(data), getattr(picture, "mime", None))

    tags = getattr(audio, "tags", None)
    if not tags:
        return None, None

    id3_pictures = getattr(tags, "getall", None)
    if callable(id3_pictures):
        pictures = id3_pictures("APIC")
        if pictures:
            picture = pictures[0]
            data = getattr(picture, "data", None)
            if data:
                return bytes(data), _image_mime(bytes(data), getattr(picture, "mime", None))

    for key in ("covr", "metadata_block_picture"):
        values = tags.get(key)
        if not values:
            continue
        picture = values[0] if isinstance(values, (list, tuple)) else values
        if key == "metadata_block_picture" and isinstance(picture, str):
            try:
                from mutagen.flac import Picture

                picture = Picture(base64.b64decode(picture))
            except (ValueError, MutagenError):
                continue
        data = getattr(picture, "data", picture)
        if isinstance(data, bytes) and data:
            preferred = None
            image_format = getattr(picture, "imageformat", None)
            if image_format is not None:
                preferred = "image/png" if int(image_format) == 1 else "image/jpeg"
            return data, _image_mime(data, preferred)

    return None, None


def read_metadata(file_path: str | Path) -> Track:
    """Lit les tags audio ; utilise le nom du fichier si les tags manquent."""
    path = Path(file_path).expanduser().resolve()
    fallback_title = path.stem
    tags = None
    duration = 0.0
    artwork = None
    artwork_mime = None

    try:
        audio = MutagenFile(path, easy=True)
        if audio is not None:
            tags = audio.tags
            if audio.info is not None:
                duration = max(0.0, float(audio.info.length))

        raw_audio = MutagenFile(path, easy=False)
        if raw_audio is not None:
            artwork, artwork_mime = _extract_artwork(raw_audio)
            raw_tags = raw_audio.tags
            if raw_tags and any(
                _tag_value(tags, name, "") == ""
                for name in ("title", "artist", "album")
            ):
                tags = _CombinedTags(tags, raw_tags)
            if duration == 0 and raw_audio.info is not None:
                duration = max(0.0, float(raw_audio.info.length))
    except (OSError, MutagenError, ValueError):
        pass

    return Track(
        path=str(path),
        title=_tag_value(tags, "title", fallback_title),
        artist=_tag_value(tags, "artist", "Artiste inconnu"),
        album=_tag_value(tags, "album", "Album inconnu"),
        duration=duration,
        artwork=artwork,
        artwork_mime=artwork_mime,
    )


class _CombinedTags:
    def __init__(self, easy_tags: Any, raw_tags: Any) -> None:
        self._tag_sets = (easy_tags, raw_tags)

    def get(self, name: str) -> Any:
        for tags in self._tag_sets:
            if tags:
                value = tags.get(name)
                if value is not None:
                    return value
        return None

    def items(self):
        for tags in self._tag_sets:
            if tags:
                yield from tags.items()
